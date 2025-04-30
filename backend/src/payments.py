import stripe

from src.config import settings
from src.db import models


def create_checkout_session(order: models.Order):
    metadata = {
        "order_id": str(order.id),
    }

    line_items = [
        {
            "price_data": {
                "currency": "uah",
                "unit_amount": int(item.total_price / item.quantity),
                "product_data": {
                    "name": item.product.title
                },
            },
            "quantity": item.quantity
        }
        for item in order.items]

    return stripe.checkout.Session.create(
        line_items=line_items,
        currency="uah",
        mode="payment",
        metadata=metadata,
        payment_intent_data={
            "metadata": metadata
        },
        success_url=settings.PAYMENT_SUCCESS_REDIRECT_URL,
        api_key=settings.STRIPE_SECRET_KEY
    )
