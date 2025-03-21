from fastapi import APIRouter, status

from src.crud import OrderCRUD, ProductCRUD, AddressCRUD
from src.custom_types import OrderStatus
from src.db.models import Order
from src.permissions import ConfirmedEmail, AdminRole
from src.schemas.client_secret import ClientSecret
from src.schemas.message import Message
from src.schemas.order import OrderIn
from src.deps import CurrentUserDep, SessionDep
from src.custom_exceptions import (
    ResourceDoesNotExistError,
    NotEnoughRightsError,
)
from src.utils import create_payment_intent

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=ClientSecret,
             dependencies=[ConfirmedEmail])
async def create_order(user: CurrentUserDep, order: OrderIn, db: SessionDep):
    address = await AddressCRUD.get(order.address_id, db)
    if address.user_id != user.id:
        raise NotEnoughRightsError("Address does not belong to the user")

    existing_products = await ProductCRUD.get_all(list(map(lambda i: i.product_id, order.items)), db=db)
    if len(existing_products) != len(order.items):
        raise ResourceDoesNotExistError("Product with the given id does not exist")

    order = await OrderCRUD.create(Order(
        **order.model_dump(),
        user_id=user.id
    ), db)
    payment_intent = create_payment_intent(order)
    return ClientSecret(client_secret=payment_intent.client_secret)


@router.post('/{order_id}/cancel', status_code=status.HTTP_200_OK, response_model=Message)
async def cancel_order(order_id: int, user: CurrentUserDep, db: SessionDep):
    order = await OrderCRUD.get(order_id, db)
    if order.user_id != user.id:
        raise NotEnoughRightsError("User is not the order owner")
    order.status = OrderStatus.CANCELLED
    return Message(message="The order cancelled")


@router.patch('/{order_id}/status', status_code=status.HTTP_200_OK, response_model=Message,
              dependencies=[AdminRole])
async def change_order_status(order_id: int, new_status: OrderStatus, db: SessionDep):
    order = await OrderCRUD.get(order_id, db)
    order.status = new_status
    return Message(message=f"The order status updated to {new_status.value}")
