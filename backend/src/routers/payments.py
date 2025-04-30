import stripe
from fastapi import APIRouter, status, Request
from fastapi.responses import RedirectResponse

from src.config import settings
from src.crud import OrderCRUD, ProductCRUD
from src.deps import SessionDep
from src.custom_exceptions import PaymentGatewayError

from src.logger import logger
from src.payments import create_checkout_session

router = APIRouter(
    prefix='/payments',
    tags=['Payments']
)


@router.get('/{order_id}/pay', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def pay(order_id: int, db: SessionDep):
    order = await OrderCRUD.get(order_id, db)

    try:
        checkout_session = create_checkout_session(order)
    except stripe.error.StripeError as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise PaymentGatewayError("Failed to create checkout session")

    return RedirectResponse(
        url=checkout_session.url
    )


@router.post('/webhook', status_code=status.HTTP_200_OK)
async def webhook(req: Request, db: SessionDep):
    try:
        await handle_event(
            stripe.Webhook.construct_event(
                payload=(await req.body()),
                sig_header=req.headers.get('stripe-signature'),
                secret=settings.STRIPE_WEBHOOK_SECRET
            ), db)
    except ValueError as e:
        logger.error("Invalid payload" + str(e))
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid signature" + str(e))


async def handle_event(event, db):
    match event.type:
        case "checkout.session.completed":
            await handle_payment_succeeded(event, db)
        case "payment_intent.payment_failed":
            await handle_payment_failed(event, db)


async def handle_payment_succeeded(event, db):
    session = event.data.object
    metadata = session['metadata']

    if order_id := metadata.get('order_id'):
        order = await OrderCRUD.get(int(order_id), db)
        order.is_paid = True


async def handle_payment_failed(event, db):
    intent = event.data.object
    metadata = intent['metadata']
    if order_id := metadata.get('order_id'):
        order = await OrderCRUD.get(int(order_id), db)

        product_ids = list(map(lambda i: i.product_id, order.items))
        products = {product.id: product for product in (await ProductCRUD.get_all(product_ids, for_update=True, db=db))}
        for item in order.items:
            products[item.product_id].quantity += item.quantity

        await OrderCRUD.delete(int(order_id), db)
