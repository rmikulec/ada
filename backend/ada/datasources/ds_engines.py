from enum import Enum

from ada.datasources.wiki import WikiSearch
from ada.datasources.general import GeneralSearch
from ada.datasources.arxiv import ArxivSearch
from ada.datasources.images import ImageWebSearch


class DatasourceEngines(Enum):
    GENERAL = GeneralSearch
    ARXIV = ArxivSearch
    WIKI = WikiSearch
    IMAGE = ImageWebSearch
