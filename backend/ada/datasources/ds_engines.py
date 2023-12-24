from enum import Enum
import logging

from ada.datasources.wiki import WikiSearch
from ada.datasources.general import GeneralSearch
from ada.datasources.arxiv import ArxivSearch
from ada.datasources.images import ImageWebSearch

logger = logging.getLogger(__name__)


class DatasourceEngines(Enum):
    GENERAL = "General"
    ARXIV = "Arxiv"
    WIKI = "Wiki"
    IMAGE = "Image"


DATASOURCE_RESOLVER = {
    "General": GeneralSearch,
    "Arxiv": ArxivSearch,
    "Wiki": WikiSearch,
    "Image": ImageWebSearch,
}
