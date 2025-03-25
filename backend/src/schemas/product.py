from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from src.config import settings
from src.schemas.base import ObjUpdate


class ProductIn(BaseModel):
    title: str = Field(max_length=32)
    description: str = Field(max_length=256)
    full_price: float = Field(ge=0)
    quantity: int = Field(gt=0, default=0)


class ProductOut(BaseModel):
    id: int
    rating: float
    final_price: float
    title: str
    description: str
    full_price: float
    images: list[str]

    @field_validator('images', mode='after')
    @classmethod
    def replace_filenames_with_urls(cls, images: list[str], info: ValidationInfo):
        return list(map(lambda filename: f"{settings.IMAGES_BASE_URL}{info.data['id']}/{filename}", images))


class ProductUpdate(ObjUpdate):
    title: Optional[str] = Field(default=None, max_length=32)
    description: Optional[str] = Field(default=None, max_length=256)
    full_price: Optional[float] = Field(default=None, ge=0)
    discount: Optional[float] = Field(default=None, ge=0, le=100)
    is_active: Optional[bool] = Field(default=None)
    quantity: Optional[int] = Field(default=None, gt=0)
