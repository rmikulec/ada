from scixplain.datasources.base import AsyncWebSource
from scixplain.datasources.engines import SearchEngines
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


class GeneralSearch(AsyncWebSource):
    def __init__(self, search_terms: List[str], max_results: int = 3):
        super().__init__(
            name="arXiv Search",
            description="Searches the web for related articles to user's question",
            resource_description="The name of the article found in the search.",
            search_terms=search_terms,
            max_results=max_results,
            engine=SearchEngines.GENERAL,
        )
        self.articles = []

    def _fix_http(self, url: str):
        if url[0:6] == "http:":
            url.removeprefix("http:")
            return "https:" + url
        else:
            return url

    def _get_resource_values(self):
        return [article.title for article in self.articles]

    async def search(self):
        await self._search()

        for result in self.results:
            url = self._fix_http(result["link"])
            self.articles.append(WebSearchArticle(url=url, title=result["title"]))

    def get_content(self, resource: str):
        closest_title = difflib.get_close_matches(resource, [a.title for a in self.articles])[0]
        article = list(filter(lambda a: a.title == closest_title, self.articles))[0]
        article._parse()
        return article.export()
