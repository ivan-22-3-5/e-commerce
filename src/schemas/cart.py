from pydantic import BaseModel, field_serializer

from src.schemas.item import ItemOut, Item


class Cart(BaseModel):
    items: list[Item]
    total_price: int


class CartOut(BaseModel):
    items: list[ItemOut]
    total_price: int

    @field_serializer('total_price')
    def serialize_total_price(self, value) -> float:
        return round(value / 100, 2)
