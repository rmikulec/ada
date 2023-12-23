from scixplain.datasources.base import AsyncWebSource
from scixplain.datasources.search_engines import SearchEngines

from typing import List
import logging
import difflib

logger = logging.getLogger(__name__)


class ImageWebSearch(AsyncWebSource):
    def __init__(self, search_terms: List[str], max_results: int = 3):
        super().__init__(
            name="image_search",
            description="Searches the web for related images that may be helpful",
            resource_description="The title of the image that could be used.",
            search_terms=search_terms,
            max_results=max_results,
            engine=SearchEngines.IMAGE,
            is_image=True,
        )
        self.images = []

    async def search(self):
        logger.info("Searching for Images...")
        await self._search()
        self.images = {res["title"]: res["link"] for res in self.results}

    def _get_resource_values(self):
        return list(self.images.keys())

    def get_content(self, resource: str):
        closest_title = difflib.get_close_matches(resource, list(self.images.keys()))[0]
        image = self.images[closest_title]
        return image
