from fastapi import APIRouter, status

from src.constraints import admin_path, confirmed_email_required
from src.crud import OrderCRUD, ProductCRUD, AddressCRUD
from src.custom_types import OrderStatus
from src.db.models import Order
from src.schemas.client_secret import ClientSecret
from src.schemas.message import Message
from src.schemas.order import OrderIn
from src.deps import cur_user_dependency, db_dependency
from src.custom_exceptions import (
    ResourceDoesNotExistError,
    NotEnoughRightsError,
)
from src.utils import create_payment_intent

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@confirmed_email_required
@router.post('', status_code=status.HTTP_201_CREATED, response_model=ClientSecret)
async def create_order(user: cur_user_dependency, order: OrderIn, db: db_dependency):
    if (address := await AddressCRUD.get(order.address_id, db)) is None:
        raise ResourceDoesNotExistError("Address with the given id does not exist")
    if address.user_id != user.id:
        raise NotEnoughRightsError("Address does not belong to the user")
    for item in order.items:
        if not await ProductCRUD.get(item.product_id, db):
            raise ResourceDoesNotExistError("Product with the given id does not exist")
    order = await OrderCRUD.create(Order(
        **order.model_dump(),
        user_id=user.id
    ), db)
    payment_intent = create_payment_intent(order)
    return ClientSecret(client_secret=payment_intent.client_secret)


@router.post('/{order_id}/cancel', status_code=status.HTTP_200_OK, response_model=Message)
async def cancel_order(order_id: int, user: cur_user_dependency, db: db_dependency):
    if (order := await OrderCRUD.get(order_id, db)) is None:
        raise ResourceDoesNotExistError("Order with the given id does not exist")
    if order.user_id != user.id:
        raise NotEnoughRightsError("User is not the order owner")
    await OrderCRUD.update_status(order_id, OrderStatus.CANCELLED, db=db)
    return Message(message="The order cancelled")


@router.patch('/{order_id}/status', status_code=status.HTTP_200_OK, response_model=Message)
@admin_path
async def change_order_status(user: cur_user_dependency, order_id: int, new_status: OrderStatus, db: db_dependency):
    if not await OrderCRUD.get(order_id, db):
        raise ResourceDoesNotExistError("Order with the given id does not exist")
    await OrderCRUD.update_status(order_id, new_status, db=db)
    return Message(message=f"The order status updated to {new_status.value}")
