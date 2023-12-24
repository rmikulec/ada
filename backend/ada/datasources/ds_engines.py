from enum import Enum

from scixplain.datasources.wiki import WikiSearch
from scixplain.datasources.general import GeneralSearch
from scixplain.datasources.arxiv import ArxivSearch
from scixplain.datasources.images import ImageWebSearch


class DatasourceEngines(Enum):
    GENERAL = GeneralSearch
    ARXIV = ArxivSearch
    WIKI = WikiSearch
    IMAGE = ImageWebSearch
