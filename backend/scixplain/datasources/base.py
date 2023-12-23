from abc import ABC, abstractmethod
from typing import Dict, List

import requests

from scixplain.datasources.search_engines import SearchEngines

import logging
import aiohttp
import json
import os
import asyncio

logger = logging.getLogger(__name__)


class SearchNotRun(Exception):
    def __init__(self):
        self.message = "In order to export a WebSource as an OpenAI Tool, the 'search' method must be called with 'await'."
        super().__init__(self.message)


class Datasource:
    def __init__(
        self,
        name: str,
        description: str,
        resource_description: str,
        search_terms: List[str],
        max_results: int = 10,
    ):
        self.name = name
        self.description = description
        self.resource_description = resource_description
        self.search_terms = search_terms
        self.max_results = max_results

        self.results = []

    def _search(self):
        pass

    def _get_resource_values(self):
        pass

    @property
    def tool_spec(self):
        if len(self.results) == 0:
            raise SearchNotRun()
        else:
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "resource": {
                                "type": "string",
                                "description": self.resource_description,
                                "enum": self._get_resource_values(),
                            }
                        },
                    },
                },
            }

    def search(self):
        pass

    def get_content(self, resource: str) -> dict:
        pass


class AsyncDatasource:
    def __init__(
        self,
        name: str,
        description: str,
        resource_description: str,
        search_terms: List[str],
        max_results: int = 10,
    ):
        self.name = name
        self.description = description
        self.resource_description = resource_description
        self.search_terms = search_terms
        self.max_results = max_results

        self.results = []

    @abstractmethod
    async def _search(self):
        pass

    @abstractmethod
    def _get_resource_values(self):
        pass

    @property
    def tool_spec(self):
        if len(self.results) == 0:
            raise SearchNotRun()
        else:
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "resource": {
                                "type": "string",
                                "description": self.resource_description,
                                "enum": self._get_resource_values(),
                            }
                        },
                    },
                },
            }

    @abstractmethod
    async def search(self):
        pass

    @abstractmethod
    async def get_content(self, resource: str) -> dict:
        pass


class AsyncWebSource(AsyncDatasource, ABC):
    def __init__(
        self,
        name: str,
        description: str,
        resource_description: str,
        search_terms: List[str],
        engine: SearchEngines,
        max_results: int = 10,
    ):
        super().__init__(
            name=name,
            description=description,
            resource_description=resource_description,
            search_terms=search_terms,
            max_results=max_results,
        )

        self.engine = engine

    def _test_url(self, url: str):
        try:
            logger.debug(f"Testing {url}...")
            res = requests.get(url)
            return res.status_code in [200, 201, 202, 203]
        except:
            return False

    async def _search_per_term(self, term: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url="https://www.googleapis.com/customsearch/v1",
                params={
                    "key": os.environ["GOOGLE_KEY"],
                    "cx": self.engine.value,
                    "q": term,
                    "count": self.max_results,
                },
            ) as res:
                results = json.loads(await res.text())

                for res in results["items"]:
                    if self._test_url(res["link"]):
                        self.results.append(res)

    async def _search(self):
        await asyncio.gather(*[self._search_per_term(term) for term in self.search_terms])


class DatasourceReturn:
    def __init__(self, text: str, references: List[str], images: Dict[str, str]):
        self.text = text
        self.references = references
        self.images = images
