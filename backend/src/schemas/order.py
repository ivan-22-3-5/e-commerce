from datetime import datetime

from pydantic import BaseModel, Field

from src.custom_types import OrderStatus
from src.schemas.item import ItemOut, ItemIn


class OrderIn(BaseModel):
    address_id: int = Field(gt=0)
    items: list[ItemIn]


class OrderOut(BaseModel):
    id: int
    address_id: int
    status: OrderStatus
    created_at: datetime
    total_price: float
    items: list[ItemOut]
