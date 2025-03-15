from pydantic import BaseModel, Field


class ItemIn(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class ItemOut(BaseModel):
    product_id: int
    quantity: int
    total_price: float
