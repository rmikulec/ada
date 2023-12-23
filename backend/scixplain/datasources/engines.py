from enum import Enum

from scixplain.datasources.wiki import WikiSearch
from scixplain.datasources.general import GeneralSearch
from scixplain.datasources.arxiv import ArxivSearch


class SearchEngines(Enum):
    GENERAL = "950f3256407244f28"
    ARXIVE = "a06016d8e362843b8"
    WIKI = "746a8afb89774424e"


class DatasourceEngines(Enum):
    GENERAL = GeneralSearch
    ARXIV = ArxivSearch
    WIKI = WikiSearch
