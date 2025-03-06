from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.base import ObjUpdate


class ProductBase(BaseModel):
    title: str = Field(max_length=32)
    description: str = Field(max_length=256)
    full_price: float = Field(ge=0)


class ProductIn(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    rating: float
    final_price: float


class ProductUpdate(ObjUpdate):
    title: Optional[str] = Field(default=None, max_length=32)
    description: Optional[str] = Field(default=None, max_length=256)
    full_price: Optional[float] = Field(default=None, ge=0)
    discount: Optional[float] = Field(default=None, ge=0, le=100)
    enabled: Optional[bool] = Field(default=None)
