from openai import AsyncOpenAI
from typing import List, Union
import json
import pathlib
import logging
import pathlib
import asyncio
import tiktoken
import traceback

from ada import DEFAULT_MODEL
from ada.system_messages import BASE_MESSAGE, SEARCH_TERMS, FIX_JSON
from ada.datasources.ds_engines import DatasourceEngines
from ada.datasources.base import AsyncDatasource, Datasource
from ada.models import ArticleLength


logger = logging.getLogger(__name__)


class FunctionNameExists(Exception):
    def __init__(self, func_name):
        self.message = f"Function '{func_name}' already is added to Communicator"
        super().__init__(self.message)


class InvalidDatasourceType(Exception):
    def __init__(self, ds_type, name):
        self.message = f"Datasource {name} is of invalid type {ds_type}. Please extend either AsyncDatasource or Datasource"


class AsyncCommunicator:
    def __init__(
        self,
        age: int,
        experience: str,
        system_template: str = BASE_MESSAGE,
        max_tokens=4_096,
        datasources: List[DatasourceEngines] = [],
        min_resources: int = 3,
        n_search_terms: int = 3,
        article_length: ArticleLength = ArticleLength.LONG,
    ):
        self.client = AsyncOpenAI()
        self.max_tokens = max_tokens

        self.system_template = system_template
        self.age = age
        self.experience = experience
        self.datasources = datasources
        self.n_search_terms = n_search_terms
        self.n_datasources = len(datasources)

        self.refs_used = []

        # Create system message
        self.system_message = system_template.format(
            age=self.age,
            experience=self.experience,
            min_resources=min_resources,
            article_length=article_length.value,
        )
        self.system_message_n_tokens = self._get_num_tokens(self.system_message)

        if self.system_message_n_tokens >= 50_000:
            raise Exception(f"Too many tokens, try reducing pages: {self.system_message_n_tokens}")

        self.messages = [
            {"role": "system", "content": self.system_message},
        ]

        self.tools = []
        self.function_mapping = {}

    def _add_question(self, question: str):
        self.messages.append({"role": "user", "content": question})

    async def _get_search_terms(self, question: str):
        response = await self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": SEARCH_TERMS},
                {"role": "user", "content": question},
            ],
            max_tokens=50,
        )

        message = response.choices[0].message.content
        return json.loads(message)[: self.n_search_terms]

    async def _set_tools(self, datasources: List[AsyncDatasource]):
        async_operations = [
            datasource.search()
            for datasource in datasources
            if isinstance(datasource, AsyncDatasource)
        ]

        await asyncio.gather(*async_operations)

        for datasource in filter(lambda d: isinstance(d, AsyncDatasource), datasources):
            try:
                self.tools.append(datasource.tool_spec)
                self.function_mapping[datasource.name] = datasource.get_content
            except Exception as err:
                logger.error(f"Tool {datasource.name} not added: \n {traceback.format_exc()}")

        for datasource in filter(lambda d: isinstance(d, Datasource), datasources):
            try:
                datasource.search()
                self.tools.append(datasource.tool_spec)
                self.function_mapping[datasource.name] = datasource.get_content
            except Exception as err:
                logger.error(f"Tool {datasource.name} not added: \n {traceback.format_exc()}")

    def _get_num_tokens(self, text):
        encoder = tiktoken.encoding_for_model(DEFAULT_MODEL)
        return len(encoder.encode(text))

    def _call_tool(self, tool_name, **kwargs):
        try:
            content = self.function_mapping[tool_name](**kwargs)
            content["ref_type"] = tool_name
            self.refs_used.append(content)
            return json.dumps(content)
        except Exception as err:
            logger.error(f"Tool {tool_name} failed: {traceback.format_exc()}")
            return json.dumps(
                {
                    "tool_name": tool_name,
                    "content": "Failed to execute. Please use a different tool or resource",
                }
            )

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
                logger.info(f"Calling {tool_name} with {func_args}")
                content = self._call_tool(tool_name=tool_name, **func_args)
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": content,
                }
                self.messages.append(tool_message)
            await self._call_openai()

    def _export_results(self, question, export_path: Union[pathlib.Path, str]):
        last_message = self.messages[-1]

        if type(last_message) == dict:
            md = self.messages[-1]["content"]
        else:
            md = self.messages[-1].content

        export_path = pathlib.Path(export_path)
        export_path.mkdir(exist_ok=True, parents=True)
        (export_path / question.lower().replace(" ", "-")).write_text(md)

    async def _fix_json(self, json_string: str):
        return await self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": FIX_JSON},
                {"role": "user", "content": json_string},
            ],
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )

    async def _verify_results(self):
        last_message = self.messages[-1]

        if type(last_message) == dict:
            content = last_message["content"]
        else:
            content = last_message.content
        try:
            response = json.loads(content)
            return response
        except json.JSONDecodeError:
            logger.warning("JSON Decode Failed; Recalling OpenAI to fix...")
            response = await self._fix_json(content)
            return self._verify_results(response.choices[0].message.content)

    async def ask(self, question: str, export_path: Union[pathlib.Path, str] = None):
        logger.info(f"Question asked: {question}")
        self._add_question(question=question)
        terms = await self._get_search_terms(question=question)
        logger.info(f"Search terms: {terms}")
        # Search with the question as well
        terms.append(question)
        logger.info("Setting up tools")
        datasources = [datasource(search_terms=terms) for datasource in self.datasources]
        await self._set_tools(datasources=datasources)
        logger.info("Tools:" + json.dumps(self.tools, indent=4))
        await self._call_openai()

        if export_path:
            self._export_results(question=question, export_path=export_path)

        return await self._verify_results()
