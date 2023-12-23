from scixplain.datasources.base import AsyncDatasource
import aiohttp
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List
import json
import os
import difflib
import requests

import newspaper


logger = logging.getLogger(__name__)


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
        try:
            article.download()
        except newspaper.ArticleException:
            html = requests.get(
                url=self.url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
                },
            )
            article.download(input_html=html)
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

    async def _test_url(self, url: str):
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=url) as res:
                    await res.text()
                    return res.status not in [200, 201, 202, 203]
            except:
                return False
        """
        try:
            logger.debug(f"Testing {url}...")
            res = requests.get(url)
            return res.status_code in [200, 201, 202, 203]
        except:
            return False

    def _fix_http(self, url: str):
        if url[0:6] == "http:":
            url.removeprefix("http:")
            return "https:" + url
        else:
            return url

    async def set_data(self):
        search_results = await self._search()
        search_results = [
            result for result in search_results["items"] if await self._test_url(result["link"])
        ]

        for result in search_results:
            url = self._fix_http(result["link"])
            self.articles.append(WebSearchArticle(url=url, title=result["title"]))

    def get_data(self, title: str):
        closest_title = difflib.get_close_matches(title, [a.title for a in self.articles])[0]
        article = list(filter(lambda a: a.title == closest_title, self.articles))[0]
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
                            "description": "The title of the article to get from",
                            "enum": [article.title for article in self.articles],
                        },
                    },
                    "required": ["title"],
                },
            },
        }

    @classmethod
    async def search(cls, question: str, n_articles: int, engine: SearchEngines):
        search = cls(question=question, n_articles=n_articles, engine=engine)

        await search.set_data()
        return search.articles
