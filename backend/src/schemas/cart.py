from pydantic import BaseModel

from src.schemas.item import ItemOut, Item


class Cart(BaseModel):
    items: list[Item]
    total_price: float


class CartOut(BaseModel):
    items: list[ItemOut]
    total_price: float
