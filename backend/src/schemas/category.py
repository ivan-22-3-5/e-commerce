from pydantic import BaseModel, field_validator, Field

from src.config import rules


class CategoryIn(BaseModel):
    name: str = Field(max_length=rules.MAX_CATEGORY_NAME_LENGTH)

    @field_validator("name")
    @classmethod
    def to_lower_case(cls, v) -> str:
        return v.lower()


class CategoryOut(BaseModel):
    id: int
    name: str
