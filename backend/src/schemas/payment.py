from pydantic import BaseModel, Field
from decimal import Decimal


class PaymentIn(BaseModel):
    user_id: int
    order_id: int
    amount: Decimal = Field(ge=0, decimal_places=2)
    currency: str = Field(max_length=3)
    payment_method: str
    intent_id: str
