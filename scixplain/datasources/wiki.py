import wikipedia
import re
from bs4 import BeautifulSoup

from typing import Dict, List


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
                    return [int(num) for num in re.findall(r"\d+", s)][0]

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

        return {
            "text": section_text,
            "references": dict(
                sorted({i: self.indexed_refs[i] for i in section_citations}.items())
            ),
        }
