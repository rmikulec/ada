from bs4 import BeautifulSoup
import aiohttp
import re
import os
import json
from dataclasses import dataclass
from scixplain.datasources.base import AsyncDatasource


@dataclass
class BritannicaDatabaseEntry:
    article_id: int
    article_type_id: int
    title: str
    last_updated: str

    async def get_article(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://syndication.api.eb.com/production/article/{self.article_id}/xml",
                headers={"accept": "application/json", "x-api-key": os.getenv("BRITT_KEY_1")},
            ) as res:
                return await res.text()


class BritannicaDatabase:
    def __init__(
        self,
        article_type_id: int,
        cateogry_id: int = None,
        last_update: str = None,
    ):
        self.article_type_id = article_type_id
        self.category_id = cateogry_id
        self.last_update = last_update

    async def _query_all(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url="https://syndication.api.eb.com/production/articles",
                params={
                    "articleTypeId": 1,
                },
                headers={"accept": "application/json", "x-api-key": os.getenv("BRITT_KEY_1")},
            ) as res:
                results = json.loads(await res.text())

                self.data = {
                    result["articleId"]: BritannicaDatabaseEntry(
                        article_id=result["articleId"],
                        article_type_id=result["articleTypeId"],
                        title=result["title"],
                        last_updated=result["lastUpdated"],
                    )
                    for result in results["articles"]
                }

    def __getitem__(self, id):
        return self.data[id]

    @classmethod
    async def create_britt_db(
        cls,
        article_type_id: int,
        cateogry_id: int = None,
        last_update: str = None,
    ):
        class_instance = cls(
            article_type_id=article_type_id, cateogry_id=cateogry_id, last_update=last_update
        )

        await class_instance._query_all()

        return class_instance


@dataclass
class BritannicaSearchResult:
    title: str
    url: str
    data_topic_id: int


class BritannicaSearch(AsyncDatasource):
    def __init__(self, question: str, n_pages: str):
        self.question = question
        self.n_pages = n_pages
        self.results = []

    async def _get_page(self, question: str):
        with aiohttp.ClientSession() as session:
            res = session.get(
                url="https://www.britannica.com/search", params={"query": self.question}
            )

            return await res.text()

    async def set_data(self):
        html = await self._get_page(self.question)
        search_page = BeautifulSoup(html)
        results_r = re.compile("RESULT-([-09]*)")

        def _remove_escape_characters(input_string):
            return "".join(char for char in input_string if char.isprintable())

        for li_item in search_page.findAll("li", {"class": results_r}):
            link_item = li_item.find("a")

            self.results.append(
                BritannicaSearch(
                    title=_remove_escape_characters(link_item.text),
                    url=link_item.get_attribute_list(key="href")[0],
                    data_topic_id=li_item.get_attribute_list(key="data-topic-id")[0],
                )
            )
