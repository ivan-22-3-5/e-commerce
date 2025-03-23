from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.base import ObjUpdate
from src.schemas.image import ProductImageOut


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

    images: list[ProductImageOut]


class ProductUpdate(ObjUpdate):
    title: Optional[str] = Field(default=None, max_length=32)
    description: Optional[str] = Field(default=None, max_length=256)
    full_price: Optional[float] = Field(default=None, ge=0)
    discount: Optional[float] = Field(default=None, ge=0, le=100)
    enabled: Optional[bool] = Field(default=None)
    quantity: Optional[int] = Field(default=None, gt=0)
