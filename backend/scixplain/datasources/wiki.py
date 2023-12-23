import wikipedia
import logging
import re
from bs4 import BeautifulSoup

from typing import Dict, List

from scixplain.datasources.base import Datasource

logger = logging.getLogger(__name__)


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
            "sections": list(self.indexed_content.keys()),
            "url": self.url,
            "references": {i + 1: ref for i, ref in enumerate(self.references)},
        }

        return data


class WikiSearch(Datasource):
    def __init__(self, search_terms: List[str], max_results: int = 10):
        super().__init__(
            name="wikipedia_search",
            description="Retrieve sections of articles from wikipedia.",
            resource_description="The {page}/{section} wiki section to retrieve content from.",
            search_terms=search_terms,
            max_results=max_results,
        )

        self.pages = []

    def _search(self):
        potential_pages = [wikipedia.search(term)[0] for term in self.search_terms]

        potential_pages = list(set(potential_pages))
        self.results.extend(potential_pages[0 : self.max_results])

    def _get_resource_values(self):
        section_enums = []

        for page in self.pages:
            sections = list(page.indexed_content.keys())
            for section in sections:
                enum = f"{page.title}/{section}"
                if enum not in section_enums:
                    section_enums.append(enum)

        return section_enums

    def search(self):
        logger.info("Searching Wiki....")
        self._search()
        self.pages.extend([WikiPage(title=title) for title in self.results])

    def get_content(self, resource: str):
        title, section = resource.split("/")
        page = list(filter(lambda p: p.title == title, self.pages))[0]
        section_content = page.get_section_content(section)
        section_content["images"] = page.image_captions
        section_content["title"] = page.title
        return section_content
