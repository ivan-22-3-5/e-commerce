from fastapi import APIRouter, status, Depends

from src.custom_types import OrderStatus
from src.permissions import AdminRole
from src.schemas.filtration import PaginationParams, OrderFilter
from src.schemas.message import Message
from src.schemas.order import OrderOut
from src.deps import CurrentUserDep, CartServiceDep, OrderServiceDep
from src.custom_exceptions import (
    EmptyCartError, NotEnoughRightsError,
)

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=OrderOut)
async def create_order(user: CurrentUserDep, order_service: OrderServiceDep, cart_service: CartServiceDep):
    cart = await cart_service.get_cart(user.id)

    if len(cart.items) == 0:
        raise EmptyCartError("The user's cart is empty")

    order = await order_service.create_order(user.id, cart)

    await cart_service.clear_cart(user.id)

    return order


@router.post('/{order_id}/cancel', status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: int, user: CurrentUserDep, order_service: OrderServiceDep):
    order = await order_service.get_order(order_id)
    if order.user_id != user.id:
        raise NotEnoughRightsError("User is not the order owner")
    await order_service.cancel_order(order_id, user.id)


@router.patch('/{order_id}/status', status_code=status.HTTP_200_OK, response_model=Message,
              dependencies=[AdminRole])
async def change_order_status(order_id: int, new_status: OrderStatus, order_service: OrderServiceDep):
    order = await order_service.get_order(order_id)
    order.status = new_status
    return Message(message=f"The order status updated to {new_status.value}")


@router.get('/', response_model=list[OrderOut], status_code=status.HTTP_200_OK,
            dependencies=[AdminRole])
async def get_orders(order_service: OrderServiceDep,
                     filter: OrderFilter = Depends(),
                     pagination: PaginationParams = Depends()):
    return await order_service.get_orders(filter=filter, pagination=pagination)
