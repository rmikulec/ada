from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict

from uuid import UUID, uuid4
from enum import Enum

from scixplain.config import MAX_TOKENS


class ResourceTypes(Enum):
    WIKIPEDIA = "wiki"


class AgeNotValidError(Exception):
    def __init__(self, age) -> None:
        self.message = f"Provided age: {age} not within valid range: 3-120 years."


class AnswerConfig(BaseModel):
    max_tokens: Optional[int] = MAX_TOKENS
    n_pages: Optional[int] = 2
    n_sections: Optional[int] = 3


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
    sections: List[str]
    references: List[str]
    type: ResourceTypes


class QuestionResponse(BaseModel):
    markdown: str
    resources: List[ResourceUsed]
