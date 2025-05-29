from pydantic import BaseModel, Field, field_serializer


class Item(BaseModel):
    product_id: int
    quantity: int
    total_price: int


class ItemIn(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class ItemOut(BaseModel):
    product_id: int
    quantity: int
    total_price: int

    @field_serializer('total_price')
    def serialize_total_price(self, value) -> float:
        return round(value / 100, 2)
