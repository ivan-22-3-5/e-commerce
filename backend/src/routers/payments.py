import stripe
from fastapi import APIRouter, status, Request

from src.config import settings
from src.crud import OrderCRUD, PaymentCRUD
from src.db.models import Payment
from src.deps import db_dependency
from src.custom_exceptions import (
    InvalidPayloadError,
    InvalidSignatureError
)

router = APIRouter(
    prefix='/stripe',
    tags=['stripe']
)


@router.post('/webhook', status_code=status.HTTP_200_OK)
async def webhook(req: Request, db: db_dependency):
    payload = await req.body()
    sig_header = req.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise InvalidPayloadError("Invalid payload" + str(e))
    except stripe.error.SignatureVerificationError as e:
        raise InvalidSignatureError("Invalid signature" + str(e))
    await handle_event(event, db)


async def handle_event(event, db):
    match event.type:
        case "payment_intent.succeeded":
            await handle_payment_succeeded(event, db)
        case "payment_intent.payment_failed":
            await handle_payment_failed(event)


async def handle_payment_succeeded(event, db):
    intent = event.data.object
    metadata = intent['metadata']
    if order_id := metadata.get('order_id'):
        order = await OrderCRUD.get(int(order_id), db)
        order.is_paid = True
        await PaymentCRUD.create(Payment(
            user_id=int(metadata.get('user_id')),
            order_id=int(order_id),
            amount=float(intent['amount']) / 100,
            currency=intent['currency'],
            payment_method=intent['payment_method'],
            intent_id=intent['id']
        ), db)


async def handle_payment_failed(event):
    intent = event.data.object
    error_message = intent['last_payment_error']['message'] if intent.get('last_payment_error') else None
    print("Failed: ", intent['id'], error_message)
