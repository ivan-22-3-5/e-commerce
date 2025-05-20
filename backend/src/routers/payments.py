import stripe
from fastapi import APIRouter, status, Request
from fastapi.responses import RedirectResponse

from src.config import settings
from src.deps import OrderServiceDep, ProductServiceDep
from src.custom_exceptions import PaymentGatewayError

from src.logger import logger
from src.payments import create_checkout_session

router = APIRouter(
    prefix='/payments',
    tags=['Payments']
)


@router.get('/{order_id}/pay', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def pay(order_id: int, order_service: OrderServiceDep):
    order = await order_service.get_order(order_id)

    try:
        checkout_session = create_checkout_session(order)
    except stripe.error.StripeError as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise PaymentGatewayError("Failed to create checkout session")

    return RedirectResponse(
        url=checkout_session.url
    )


@router.post('/webhook', status_code=status.HTTP_200_OK)
async def webhook(req: Request, order_service: OrderServiceDep, product_service: ProductServiceDep):
    try:
        await handle_event(
            stripe.Webhook.construct_event(
                payload=(await req.body()),
                sig_header=req.headers.get('stripe-signature'),
                secret=settings.STRIPE_WEBHOOK_SECRET
            ), order_service)
    except ValueError as e:
        logger.error("Invalid payload" + str(e))
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid signature" + str(e))


async def handle_event(event, order_service: OrderServiceDep):
    match event.type:
        case "checkout.session.completed":
            await handle_payment_succeeded(event, order_service)
        case "payment_intent.payment_failed":
            await handle_payment_failed(event, order_service)


async def handle_payment_succeeded(event, order_service: OrderServiceDep):
    session = event.data.object
    metadata = session['metadata']

    if order_id := metadata.get('order_id'):
        order = await order_service.get_order(int(order_id))
        order.is_paid = True


async def handle_payment_failed(event, order_service: OrderServiceDep):
    intent = event.data.object
    metadata = intent['metadata']
    if order_id := metadata.get('order_id'):
        await order_service.delete_order(int(order_id))
