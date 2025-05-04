from typing import Optional

from pydantic import BaseModel, Field, field_validator, field_serializer
from pydantic_core.core_schema import ValidationInfo

from src.config import settings, rules
from src.schemas.base import ObjUpdate


class ProductIn(BaseModel):
    title: str = Field(max_length=rules.MAX_PRODUCT_TITLE_LENGTH)
    description: str = Field(max_length=rules.MAX_PRODUCT_DESCRIPTION_LENGTH)
    full_price: float = Field(ge=0)
    quantity: int = Field(gt=0, default=0)

    @field_serializer('full_price')
    def convert_price_to_int(self, v: float) -> int:
        return int(v * 100)


class ProductOut(BaseModel):
    id: int
    rating: float
    final_price: int
    title: str
    description: str
    full_price: int
    images: list[str]

    @field_serializer('full_price', 'final_price')
    def convert_price_to_float(self, v: int) -> float:
        return round(v / 100, 2)

    @field_validator('images', mode='after')
    @classmethod
    def replace_filenames_with_urls(cls, images: list[str], info: ValidationInfo):
        return list(map(lambda filename: f"{settings.IMAGES_BASE_URL}{info.data['id']}/{filename}", images))


class ProductUpdate(ObjUpdate):
    title: Optional[str] = Field(default=None, max_length=rules.MAX_PRODUCT_TITLE_LENGTH)
    description: Optional[str] = Field(default=None, max_length=rules.MAX_PRODUCT_DESCRIPTION_LENGTH)
    full_price: Optional[float] = Field(default=None, ge=0)
    discount: Optional[float] = Field(default=None, ge=0, le=100)
    is_active: Optional[bool] = Field(default=None)
    quantity: Optional[int] = Field(default=None, gt=0)

    @field_serializer('full_price')
    def convert_price_to_int(self, v: float) -> int:
        return v and int(v * 100)
