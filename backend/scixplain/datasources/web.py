from scixplain.datasources.base import AsyncDatasource
import aiohttp
from dataclasses import dataclass
from enum import Enum
from typing import List
import json
import os

import newspaper


class SearchEngines(Enum):
    WEB = "950f3256407244f28"
    ARXIVE = "a06016d8e362843b8"


@dataclass
class WebSearchArticle:
    title: str
    url: str
    text: str = None
    authors: List[str] = None
    published_date: str = None
    top_image: str = None
    images: List[str] = None
    keywords: List[str] = None
    summary: str = None

    def _parse(self):
        article = newspaper.Article(url=self.url, language="en")
        article.download()
        article.parse()

        self.text = (str(article.text),)
        self.authors = (article.authors,)
        self.published_date = (str(article.publish_date),)
        self.top_image = (str(article.top_image),)
        self.images = list(article.images)
        self.keywords = (article.keywords,)
        self.summary = str(article.summary)

    def export(self):
        return {"text": self.text, "authors": self.authors, "images": self.images}


class AsyncWebSearch(AsyncDatasource):
    def __init__(self, question: str, n_articles: int, engine: SearchEngines = SearchEngines.WEB):
        self.question = question
        self.n_articles = n_articles
        self.engine = engine
        self.articles = []

    async def _search(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url="https://www.googleapis.com/customsearch/v1",
                params={
                    "key": os.environ["GOOGLE_KEY"],
                    "cx": self.engine.value,
                    "q": self.question,
                    "count": self.n_articles,
                },
            ) as res:
                return json.loads(await res.text())

    async def set_data(self):
        search_results = await self._search()

        for result in search_results["items"]:
            self.articles.append(WebSearchArticle(url=result["link"], title=result["title"]))

    def get_data(self, title: str):
        article = list(filter(lambda a: a.title == title, self.articles))[0]
        article._parse()
        return article.export()

    def to_openai_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": f"Gets the text from one of the top {self.n_articles} results from google search",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the article from the google search",
                            "enum": [article.title for article in self.articles],
                        },
                    },
                    "required": ["route"],
                },
            },
        }

    @classmethod
    async def search(cls, question: str, n_articles: int, engine: SearchEngines):
        search = cls(question=question, n_articles=n_articles, engine=engine)

        await search.set_data()
        return search.articles
