from openai import AsyncOpenAI, OpenAI
from typing import List
import json
import pathlib
import tiktoken

from scixplain import DEFAULT_MODEL
from scixplain.system_messages import BASE_MESSAGE, BASE_MESSAGE_2
from scixplain.datasources.base import AsyncDatasource, Datasource


class FunctionNameExists(Exception):
    def __init__(self, func_name):
        self.message = f"Function '{func_name}' already is added to Communicator"
        super().__init__(self.message)


class Communicator:
    def __init__(
        self,
        initial_question: str,
        age: int,
        experience: str,
        system_template: str = BASE_MESSAGE_2,
        max_tokens=2_048,
        n_datasources: int = 3,
    ):
        self.client = OpenAI()
        self.max_tokens = max_tokens

        self.initial_question = initial_question
        self.age = age
        self.experience = experience

        # Create system message
        self.system_message = system_template.format(
            age=self.age, experience=self.experience, n_datasources=n_datasources
        )
        self.system_message_n_tokens = self._get_num_tokens(self.system_message)

        if self.system_message_n_tokens >= 50_000:
            raise Exception(f"Too many tokens, try reducing pages: {self.system_message_n_tokens}")

        self.messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": self.initial_question},
        ]

        self.tools = []
        self.function_mapping = {}

    def _get_num_tokens(self, text):
        encoder = tiktoken.encoding_for_model(DEFAULT_MODEL)
        return len(encoder.encode(text))

    def add_tool(self, tool_spec, func):
        func_name = tool_spec["function"]["name"]
        if func_name not in self.function_mapping:
            self.function_mapping[func_name] = func
            self.tools.append(tool_spec)
        else:
            raise FunctionNameExists(func_name=func_name)

    def _call_tool(self, tool_name, **kwargs):
        content = self.function_mapping[tool_name](**kwargs)
        return json.dumps(content, indent=4)

    def _call_openai(self):
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=self.messages,
            max_tokens=self.max_tokens,
            tools=self.tools,
            tool_choice="auto",
            response_format={"type": "json_object"},
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        self.messages.append(response_message)

        if tool_calls:
            for tool_call in tool_calls:
                func_args = json.loads(tool_call.function.arguments)
                tool_name = tool_call.function.name
                print(f"Calling {tool_name} with {func_args}")
                content = self._call_tool(tool_name=tool_name, **func_args)
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": content,
                }
                self.messages.append(tool_message)
            self._call_openai()

    def _export_results(self):
        last_message = self.messages[-1]

        if type(last_message) == dict:
            md = self.messages[-1]["content"]
        else:
            md = self.messages[-1].content
        root = pathlib.Path("./answers")
        root.mkdir(exist_ok=True, parents=True)
        (root / self.initial_question.lower().replace(" ", "-")).write_text(md)

    def run(self):
        self._call_openai()
        self._export_results()


class AsyncCommunicator:
    def __init__(
        self,
        initial_question: str,
        age: int,
        experience: str,
        system_template: str = BASE_MESSAGE_2,
        max_tokens=2_048,
        datasources: List[AsyncDatasource] = [],
    ):
        self.client = AsyncOpenAI()
        self.max_tokens = max_tokens

        self.initial_question = initial_question
        self.system_template = system_template
        self.age = age
        self.experience = experience
        self.datasources = datasources
        self.n_datasources = len(datasources)

        # Create system message
        self.system_message = system_template.format(
            age=self.age, experience=self.experience, n_datasources=self.n_datasources
        )
        self.system_message_n_tokens = self._get_num_tokens(self.system_message)

        if self.system_message_n_tokens >= 50_000:
            raise Exception(f"Too many tokens, try reducing pages: {self.system_message_n_tokens}")

        self.messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": self.initial_question},
        ]

        self.tools = []
        self.function_mapping = {}

    def _get_num_tokens(self, text):
        encoder = tiktoken.encoding_for_model(DEFAULT_MODEL)
        return len(encoder.encode(text))

    def add_tool(self, tool_spec, func):
        func_name = tool_spec["function"]["name"]
        if func_name not in self.function_mapping:
            self.function_mapping[func_name] = func
            self.tools.append(tool_spec)
        else:
            raise FunctionNameExists(func_name=func_name)

    def _call_tool(self, tool_name, **kwargs):
        content = self.function_mapping[tool_name](**kwargs)
        return json.dumps(content, indent=4)

    async def _call_openai(self):
        response = await self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=self.messages,
            max_tokens=self.max_tokens,
            tools=self.tools,
            tool_choice="auto",
            response_format={"type": "json_object"},
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        self.messages.append(response_message)

        if tool_calls:
            for tool_call in tool_calls:
                func_args = json.loads(tool_call.function.arguments)
                tool_name = tool_call.function.name
                print(f"Calling {tool_name} with {func_args}")
                content = self._call_tool(tool_name=tool_name, **func_args)
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": content,
                }
                self.messages.append(tool_message)
            await self._call_openai()

    def _export_results(self):
        last_message = self.messages[-1]

        if type(last_message) == dict:
            md = self.messages[-1]["content"]
        else:
            md = self.messages[-1].content
        root = pathlib.Path("./answers")
        root.mkdir(exist_ok=True, parents=True)
        (root / self.initial_question.lower().replace(" ", "-")).write_text(md)

    async def run(self):

        for datasource in self.datasources:
            if isinstance(datasource, AsyncDatasource):
                await datasource.set_data()
                tool_spec = datasource.to_openai_tool()
                self.add_tool(tool_spec=tool_spec, func=datasource.get_data)
            elif isinstance(datasource, Datasource):
                tool_spec = datasource.to_openai_tool()
                self.add_tool(tool_spec=tool_spec, func=datasource.get_data)

        await self._call_openai()
