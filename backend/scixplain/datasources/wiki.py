import wikipedia
import re
import json
from openai import OpenAI, AsyncOpenAI
from bs4 import BeautifulSoup

from typing import Dict, List

from scixplain import DEFAULT_MODEL
from scixplain.system_messages import WIKI_SEARCH_TERMS
from scixplain.datasources.base import AsyncDatasource


class WikiPage(wikipedia.WikipediaPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.html = BeautifulSoup(self.html(), features="html.parser")
        self.image_captions = self._get_all_image_captions()
        self.indexed_content = self._build_sections()
        self.indexed_refs = {i + 1: ref for i, ref in enumerate(self.references)}

    # TODO: Update function to handle thumbnail images
    def _get_all_image_captions(self) -> Dict[str, str]:
        figures = self.html.findAll(name="figure")

        data = {}

        for fig in figures:
            try:
                img_src = fig.findAll(name="a")[0].findAll(name="img")[0].attrs["src"]
                if img_src.startswith("//"):
                    img_src = "https:" + img_src
                img_caption = fig.findAll(name="figcaption")[0].text
                data[img_src] = img_caption
            except IndexError:
                pass

        return data

    # TODO: Pages can have nested sections (h3, h4, etc.)
    #   May need to update this function to recursively create an object that can tolerate these
    #   nested sections. For now, and for testing gpt, will keep this to just handle h2 sections
    def _build_sections(self) -> Dict[str, List[str]]:
        sections = {}

        current_section = "Summary"
        sections[current_section] = []

        for paragraph in list(list(self.html.children)[0].children):
            if paragraph.name == "h2":
                current_section = paragraph.find(name="span").text
                sections[current_section] = []
            elif paragraph.name == "p":
                citations = paragraph.findAll(name="sup", attrs={"class": "reference"})
                if not citations:
                    citations = []

                def __get_num_from_string(s):
                    try:
                        return [int(num) for num in re.findall(r"\d+", s)][0]
                    except IndexError:
                        return None

                sub_data = {
                    "text": paragraph.text,
                    "citations": [
                        __get_num_from_string(citation.text) for citation in list(citations)
                    ],
                }
                sections[current_section].append(sub_data)
        return sections

    def get_section_content(self, section):
        section = self.indexed_content[section]
        section_text = "\n".join([paragraph["text"] for paragraph in section])
        section_citations = []
        for paragraph in section:
            section_citations.extend(paragraph["citations"])
        section_citations = list(set(section_citations))
        section_citations = list(
            filter(lambda c: c in self.indexed_refs.keys(), section_citations)
        )
        return {
            "text": section_text,
            "references": dict(
                sorted({i: self.indexed_refs[i] for i in section_citations}.items())
            ),
        }

    def _to_json(self):
        data = {
            "title": self.title,
            "images": self.image_captions,
            "sections": list(self.indexed_content.keys()),
            "url": self.url,
            "references": {i + 1: ref for i, ref in enumerate(self.references)},
        }

        return data


class WikiSearch:
    def __init__(self, question, n_pages: int = 1, n_sections: int = 3):
        self.question = question
        self.n_pages = n_pages
        self.n_sections = n_sections

        self.client = OpenAI()
        self.search_terms = self._get_wiki_search_terms(question=question)
        self.pages = self._get_pages()

    def _get_wiki_search_terms(self, question):
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": WIKI_SEARCH_TERMS},
                {"role": "user", "content": question},
            ],
            max_tokens=50,
        )

        message = response.choices[0].message.content
        return json.loads(message)

    # TODO: Would like to update to do round robin addding.
    #   So take the first page from each term, then the second
    #   and so on
    # For now, just going to limit the terms instead of pages
    def _get_pages(self):
        potential_pages = [wikipedia.search(term)[0] for term in self.search_terms]

        potential_pages = list(set(potential_pages))
        results = potential_pages[0 : self.n_pages]
        return [WikiPage(title=result) for result in results]

    def get_content(self, route: str):
        title, section = route.split("/")
        page = list(filter(lambda p: p.title == title, self.pages))[0]
        section_content = page.get_section_content(section)
        section_content["images"] = page.image_captions
        section_content["title"] = page.title
        return section_content

    def get_section_enums(self):
        section_enums = []

        for page in self.pages:
            sections = list(page.indexed_content.keys())
            for section in sections:
                enum = f"{page.title}/{section}"
                if enum not in section_enums:
                    section_enums.append(enum)

        return section_enums


class AsyncWikiSearch(AsyncDatasource):
    def __init__(self, question, n_pages: int = 1, n_sections: int = 3):
        self.question = question
        self.n_pages = n_pages
        self.n_sections = n_sections

        self.client = AsyncOpenAI()

    async def _get_wiki_search_terms(self, question):
        response = await self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": WIKI_SEARCH_TERMS},
                {"role": "user", "content": question},
            ],
            max_tokens=50,
        )

        message = response.choices[0].message.content
        return json.loads(message)

    # TODO: Would like to update to do round robin addding.
    #   So take the first page from each term, then the second
    #   and so on
    # For now, just going to limit the terms instead of pages
    async def set_data(self):
        potential_pages = [
            wikipedia.search(term)[0]
            for term in await self._get_wiki_search_terms(question=self.question)
        ]

        potential_pages = list(set(potential_pages))
        results = potential_pages[0 : self.n_pages]
        self.pages = [WikiPage(title=result) for result in results]

    def get_data(self, route: str):
        title, section = route.split("/")
        page = list(filter(lambda p: p.title == title, self.pages))[0]
        section_content = page.get_section_content(section)
        section_content["images"] = page.image_captions
        section_content["title"] = page.title
        return section_content

    def _get_section_enums(self):
        section_enums = []

        for page in self.pages:
            sections = list(page.indexed_content.keys())
            for section in sections:
                enum = f"{page.title}/{section}"
                if enum not in section_enums:
                    section_enums.append(enum)

        return section_enums

    def to_openai_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "get_wikipedia_content",
                "description": "Gets content from a wikipedia section, including text, images, and any references used.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route": {
                            "type": "string",
                            "description": "the 'title/section' of the wikipedia page to get content from.",
                            "enum": self._get_section_enums(),
                        },
                    },
                    "required": ["route"],
                },
            },
        }
