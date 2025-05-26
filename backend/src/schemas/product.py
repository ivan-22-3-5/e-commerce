from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, field_serializer
from pydantic_core.core_schema import ValidationInfo

from src.config import settings, rules
from src.schemas.base import ObjUpdate
from src.schemas.category import CategoryOut


class ProductIn(BaseModel):
    title: str = Field(..., max_length=rules.MAX_PRODUCT_TITLE_LENGTH)
    description: str = Field(..., max_length=rules.MAX_PRODUCT_DESCRIPTION_LENGTH)
    full_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    discount: Optional[int] = Field(default=0, ge=0, le=100)
    category_ids: Optional[List[int]] = Field(default=None, description="Список ID категорій")

    @field_serializer('full_price')
    def serialize_full_price_to_int(self, v: float) -> int:
        return int(v * 100)


class ProductOut(BaseModel):
    id: int
    title: str
    description: str
    quantity: int
    full_price: int
    discount: int
    final_price: int
    rating: float
    images: List[str]
    is_active: bool
    created_at: datetime
    categories: List[CategoryOut] = []

    @field_serializer('full_price', 'final_price')
    def serialize_prices_to_float(self, v: int) -> float:
        return round(v / 100, 2)

    @classmethod
    def replace_filenames_with_urls(cls, images: List[str], info: ValidationInfo) -> List[str]:
        product_id = None
        if info.data and 'id' in info.data:
            product_id = info.data['id']

        if product_id is not None:
            return [f"{settings.IMAGES_BASE_URL}{product_id}/{filename}" for filename in images]
        return images  # pragma: no cover

    class Config:
        from_attributes = True


class ProductUpdate(ObjUpdate):
    title: Optional[str] = Field(default=None, max_length=rules.MAX_PRODUCT_TITLE_LENGTH)
    description: Optional[str] = Field(default=None, max_length=rules.MAX_PRODUCT_DESCRIPTION_LENGTH)
    full_price: Optional[float] = Field(default=None, ge=0)
    discount: Optional[int] = Field(default=None, ge=0, le=100)
    is_active: Optional[bool] = Field(default=None)
    quantity: Optional[int] = Field(default=None, ge=0)
    category_ids: Optional[List[int]] = Field(default=None, description="Список ID категорій для оновлення")

    @field_serializer('full_price', when_used='always')
    def serialize_update_full_price_to_int(self, v: Optional[float]) -> Optional[int]:
        if v is not None:
            return int(v * 100)
        return None