from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class ItemIn(ItemBase):
    pass


class ItemOut(ItemBase):
    total_price: float
