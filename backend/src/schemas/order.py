from datetime import datetime

from pydantic import BaseModel, field_serializer

from src.custom_types import OrderStatus
from src.schemas.item import ItemOut, ItemIn


class OrderIn(BaseModel):
    items: list[ItemIn]


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    created_at: datetime
    total_price: int
    items: list[ItemOut]

    @field_serializer('total_price')
    def convert_price_to_float(self, v: int) -> float:
        return round(v / 100, 2)
