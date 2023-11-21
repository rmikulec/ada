import wikipedia
from bs4 import BeautifulSoup

from typing import Dict, List


class WikiPage(wikipedia.WikipediaPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.html = BeautifulSoup(self.html(), features="html.parser")
        self.image_captions = self._get_all_image_captions()
        self.indexed_content = self._build_sections()

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

        for child in list(list(self.html.children)[0].children):
            if child.name == "h2":
                current_section = child.find(name="span").text
                sections[current_section] = []
            elif child.name == "p":
                sections[current_section].append(child.text)
        return sections
