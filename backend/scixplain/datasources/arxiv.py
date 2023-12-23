import arxiv
import pathlib
from PyPDF2 import PdfReader

from tempfile import TemporaryDirectory

from scixplain.datasources.base import AsyncDatasource
from scixplain.datasources.web import SearchEngines, AsyncWebSearch


class ArxivSearch(AsyncDatasource):
    def __init__(
        self,
        question: str,
        n_pages=3,
        criterion: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
    ):
        self.question = question
        self.n_pages = n_pages
        self.sort_criterion = criterion
        self.papers = []

    def _read_pdf(self, paper: arxiv.Result):
        with TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir, "paper.pdf")
            paper.download_pdf(dirpath=temp_dir, filename="paper.pdf")

            reader = PdfReader(temp_path)

            return {i: page.extract_text() for i, page in enumerate(reader.pages)}

    async def set_data(self):
        results = await AsyncWebSearch.search(
            question=self.question, n_articles=self.n_pages, engine=SearchEngines.ARXIVE
        )
        result_ids = [result.url.split("/")[-1] for result in results]
        search = arxiv.Search(id_list=result_ids)

        client = arxiv.Client()

        self.papers = [paper for paper in client.results(search=search)]

    def get_data(self, paper_title: str):
        paper = list(filter(lambda p: p.title == paper_title, self.papers))[0]

        return {"text": self._read_pdf(paper)}

    def to_openai_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "get_arxiv_paper",
                "description": "Gets a research paper from ArXiv.com",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "paper_title": {
                            "type": "string",
                            "description": "the title of the research paper to get",
                            "enum": [paper.title for paper in self.papers],
                        }
                    },
                    "required": ["paper_title"],
                },
            },
        }
