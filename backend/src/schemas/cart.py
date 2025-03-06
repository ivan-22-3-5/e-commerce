from pydantic import BaseModel

from src.schemas.item import ItemOut


class CartOut(BaseModel):
    items: list[ItemOut]
    total_price: float
