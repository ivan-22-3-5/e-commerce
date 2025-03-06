from pydantic import BaseModel, field_validator, Field


class CategoryIn(BaseModel):
    name: str = Field(max_length=32)

    @field_validator('name')
    @classmethod
    def to_lower_case(cls, v) -> str:
        return v.lower()
