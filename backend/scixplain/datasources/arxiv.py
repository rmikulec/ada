import arxiv
import pathlib
from PyPDF2 import PdfReader 

from tempfile import TemporaryDirectory

from scixplain.datasources.base import Datasource

class ArxivSearch(Datasource):

    def __init__(self, question: str, n_pages=3, criterion: arxiv.SortCriterion = arxiv.SortCriterion.Relevance):
        self.question = question
        self.n_pages = n_pages
        self.sort_criterion = criterion
        self.papers = self._search_papers()

    
    def _read_pdf(self, paper: arxiv.Result):
        with TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir, "paper.pdf")
            paper.download_pdf(dirpath=temp_dir, filename="paper.pdf")

            reader = PdfReader(temp_path)

            return {
                i: page.extract_text()
                for i, page in enumerate(reader.pages)
            }
        
    def _search_papers(self):
        search = arxiv.Search(
            query=self.question,
            max_results=self.n_pages,
            sort_by=self.sort_criterion
        )

        client = arxiv.Client()

        return [
            paper
            for paper in client.results(search=search)
        ]

    def get_data(self, paper_title:str):
        paper = list(filter(lambda p: p.title==paper_title, self.papers))[0]

        return self._read_pdf(paper)
    

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
                            "description": "the 'title of the research paper",
                            "enum": [paper.title for paper in self.papers],
                        }
                    },
                    "required": ["route"],
                },
            },
        }
