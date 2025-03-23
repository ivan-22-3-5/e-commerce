from pydantic import BaseModel, field_validator, Field

from src.config import settings


class ProductImageOut(BaseModel):
    id: int
    url: str = Field(validation_alias='uri')
    is_primary: bool

    @field_validator('url', mode='after')
    @classmethod
    def validate_url(cls, v):
        return settings.IMAGES_BASE_URL + v
