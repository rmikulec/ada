from enum import Enum
import logging

from scixplain.datasources.wiki import WikiSearch
from scixplain.datasources.general import GeneralSearch
from scixplain.datasources.arxiv import ArxivSearch
from scixplain.datasources.images import ImageWebSearch

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
