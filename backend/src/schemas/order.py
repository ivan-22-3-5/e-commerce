from datetime import datetime

from pydantic import BaseModel

from src.custom_types import OrderStatus
from src.schemas.item import ItemOut, ItemIn


class OrderIn(BaseModel):
    items: list[ItemIn]


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    created_at: datetime
    total_price: float
    items: list[ItemOut]
