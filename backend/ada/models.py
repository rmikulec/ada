from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict

from uuid import UUID, uuid4
from enum import Enum

from ada.config import MAX_TOKENS
from ada.datasources.ds_engines import DatasourceEngines, DATASOURCE_RESOLVER
from ada.datasources.references import ReferenceType


class ArticleLength(Enum):
    SHORT = 800
    MEDIUM = 1_600
    LONG = 3_200


class InvalidDatasourceType(Exception):
    def __init__(self, datasource):
        self.message = f"{datasource} is not a valid datasource engine."


class AgeNotValidError(Exception):
    def __init__(self, age) -> None:
        self.message = f"Provided age: {age} not within valid range: 3-120 years."


class DatasourceConfig(BaseModel):
    engine: DatasourceEngines
    max_results: Optional[int] = 3

    @validator("engine", allow_reuse=True)
    def engine_resolver(cls, value):
        if isinstance(value, DatasourceEngines):
            return DATASOURCE_RESOLVER[value.value]
        raise InvalidDatasourceType(datasource=value.value)


class AnswerConfig(BaseModel):
    max_tokens: Optional[int] = MAX_TOKENS
    max_results: Optional[int] = 5
    article_len: Optional[ArticleLength] = ArticleLength.LONG
    datasources: List[DatasourceConfig] = [
        DatasourceConfig(engine=DatasourceEngines.GENERAL),
        DatasourceConfig(engine=DatasourceEngines.ARXIV),
        DatasourceConfig(engine=DatasourceEngines.WIKI),
        DatasourceConfig(engine=DatasourceEngines.IMAGE),
    ]


class QuestionRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question: str
    age: Optional[int] = 27
    experience: Optional[str] = "Nurse"
    config: Optional[AnswerConfig] = AnswerConfig()

    @validator("age")
    def age_must_be_valid(cls, v):
        if v < 3 and v > 120:
            raise AgeNotValidError(age=v)
        return v


class Reference(BaseModel):
    name: str
    link: str
    type: ReferenceType


class GPTArticleSection(BaseModel):
    header: str
    markdown: str
    image: Optional[str] = None
    references: List[int]


class GPTArticleResponse(BaseModel):
    sections: List[GPTArticleSection]


class QuestionResponse(BaseModel):
    article: GPTArticleResponse
    references: List[Reference]
