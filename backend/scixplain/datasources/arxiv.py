import arxiv
import pathlib
import logging
from PyPDF2 import PdfReader

from tempfile import TemporaryDirectory
from typing import List

from scixplain.datasources.base import AsyncWebSource
from scixplain.datasources.search_engines import SearchEngines

logger = logging.getLogger(__name__)


class ArxivSearch(AsyncWebSource):
    def __init__(
        self,
        search_terms: List[str],
        max_results: int = 3,
        criterion: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
    ):
        super().__init__(
            name="arxiv_search",
            description="Retrieve published papers form the arXiv",
            resource_description="The name of the paper that is wanted.",
            search_terms=search_terms,
            max_results=max_results,
            engine=SearchEngines.ARXIVE,
        )
        self.sort_criterion = criterion
        self.papers = {}

    def _read_pdf(self, paper: arxiv.Result):
        with TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir, "paper.pdf")
            paper.download_pdf(dirpath=temp_dir, filename="paper.pdf")

            reader = PdfReader(temp_path)

            return {i: page.extract_text() for i, page in enumerate(reader.pages)}

    def _get_resource_values(self):
        return list(self.papers.keys())

    async def search(self):
        logger.info("Searching the arXiv...")
        await self._search()
        self.papers = {}
        for result in self.results:
            try:
                title = result["pagemap"]["metatags"][0]["citation_title"]
                id = result["pagemap"]["metatags"][0]["citation_arxiv_id"]
                self.papers[title] = id
            except KeyError:
                pass

    def get_content(self, resource: str) -> dict:
        client = arxiv.Client()
        paper_id = self.papers[resource]
        search = arxiv.Search(id_list=[paper_id])
        paper = [paper for paper in client.results(search=search)][0]

        return {"text": self._read_pdf(paper)}
