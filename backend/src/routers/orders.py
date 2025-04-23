from fastapi import APIRouter, status

from src.crud import OrderCRUD, ProductCRUD, CartCRUD
from src.custom_types import OrderStatus
from src.db.models import Order
from src.permissions import AdminRole
from src.schemas.message import Message
from src.schemas.order import OrderOut
from src.deps import CurrentUserDep, SessionDep
from src.custom_exceptions import (
    ResourceDoesNotExistError,
    NotEnoughRightsError,
    InsufficientStockError, InvalidOrderStatusError,
)

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=OrderOut)
async def create_order(user: CurrentUserDep, db: SessionDep):
    cart = await CartCRUD.get_cart(user.id, db)

    product_ids = list(map(lambda i: i.product_id, cart.items))
    products = {product.id: product for product in (await ProductCRUD.get_all(product_ids,
                                                                              for_update=True,
                                                                              db=db))}

    for item in cart.items:
        product = products.get(item.product_id, None)

        if product is None:
            raise ResourceDoesNotExistError(f"Product with id {item.product_id} does not exist")

        if product.quantity < item.quantity:
            raise InsufficientStockError(f"Insufficient stock for product ID {item.product_id}")

        product.quantity -= item.quantity

    order = await OrderCRUD.create(Order(
        items=cart.items,
        user_id=user.id
    ), db)

    await CartCRUD.clear(user.id, db)

    return order


@router.post('/{order_id}/cancel', status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: int, user: CurrentUserDep, db: SessionDep):
    order = await OrderCRUD.get(order_id, db)
    if order.user_id != user.id:
        raise NotEnoughRightsError("User is not the order owner")

    # TODO: reconsider order cancellation behavior for different statuses
    if order.status != OrderStatus.PENDING:
        raise InvalidOrderStatusError("Order cannot be cancelled")

    product_ids = list(map(lambda i: i.product_id, order.items))
    products = {product.id: product for product in (await ProductCRUD.get_all(product_ids,
                                                                              for_update=True,
                                                                              db=db))}
    for item in order.items:
        products[item.product_id].quantity += item.quantity

    order.status = OrderStatus.CANCELLED


@router.patch('/{order_id}/status', status_code=status.HTTP_200_OK, response_model=Message,
              dependencies=[AdminRole])
async def change_order_status(order_id: int, new_status: OrderStatus, db: SessionDep):
    order = await OrderCRUD.get(order_id, db)
    order.status = new_status
    return Message(message=f"The order status updated to {new_status.value}")
