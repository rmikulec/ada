from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict

from uuid import UUID, uuid4
from enum import Enum

from scixplain.config import MAX_TOKENS
from scixplain.datasources.ds_engines import DatasourceEngines


class AgeNotValidError(Exception):
    def __init__(self, age) -> None:
        self.message = f"Provided age: {age} not within valid range: 3-120 years."


class DatasourceConfig(BaseModel):
    type: DatasourceEngines
    parameters: dict


class AnswerConfig(BaseModel):
    max_tokens: Optional[int] = MAX_TOKENS
    max_results: Optional[int] = 5
    datasources: List[DatasourceConfig] = [
        DatasourceConfig(type=DatasourceEngines.GENERAL),
        DatasourceConfig(type=DatasourceEngines.ARXIV),
        DatasourceConfig(type=DatasourceEngines.WIKI),
    ]


class QuestionRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question: str
    age: Optional[int] = 18
    experience: Optional[str] = "None"
    config: Optional[AnswerConfig] = AnswerConfig()

    @validator("age")
    def age_must_be_valid(cls, v):
        if v < 3 and v > 120:
            raise AgeNotValidError(age=v)
        return v


class ResourceUsed(BaseModel):
    url: str
    references: List[str] = []
    type: DatasourceEngines


class QuestionResponse(BaseModel):
    markdown: str
    references: Dict[int, str]
    resources: List[ResourceUsed]
