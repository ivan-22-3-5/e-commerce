from fastapi import APIRouter, status

from src.crud import OrderCRUD
from src.custom_exceptions import (
    NotEnoughRightsError,
)
from src.custom_types import OrderStatus
from src.db.models import Order
from src.deps import CurrentUserDep, SessionDep
from src.permissions import AdminRole
from src.schemas.message import Message
from src.schemas.order import OrderIn

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_order(user: CurrentUserDep, order: OrderIn, db: SessionDep):
    return await OrderCRUD.create(Order(
        **order.model_dump(),
        user_id=user.id
    ), db)


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
