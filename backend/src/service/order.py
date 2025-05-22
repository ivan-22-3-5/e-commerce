from src.crud import OrderCRUD, CartItemCRUD, ProductCRUD
from src.custom_exceptions import ResourceDoesNotExistError, InsufficientStockError, NotEnoughRightsError, \
    InvalidOrderStatusError
from src.custom_types import OrderStatus
from src.db.models import Order
from src.schemas.cart import Cart


class OrderService:
    def __init__(self, order_crud: OrderCRUD, cart_item_crud: CartItemCRUD, product_crud: ProductCRUD):
        self.order_crud = order_crud
        self.cart_item_crud = cart_item_crud
        self.product_crud = product_crud

    async def create_order(self, user_id: int, cart: Cart):
        product_ids = list(map(lambda i: i.product_id, cart.items))
        products = {product.id: product for product in (await self.product_crud.get_all(product_ids, for_update=True))}

        for item in cart.items:
            product = products.get(item.product_id, None)

            if product is None:
                raise ResourceDoesNotExistError(f"Product with id {item.product_id} does not exist")

            if product.quantity < item.quantity:
                raise InsufficientStockError(f"Insufficient stock for product ID {item.product_id}")

            product.quantity -= item.quantity

        order = await self.order_crud.create(Order(
            items=cart.items,
            user_id=user_id
        ))

        return order

    async def cancel_order(self, order_id: int, user_id: int):
        order = await self.order_crud.get(order_id)
        if order.user_id != user_id:
            raise NotEnoughRightsError("User is not the order owner")

        # TODO: reconsider order cancellation behavior for different statuses
        if order.status != OrderStatus.PENDING:
            raise InvalidOrderStatusError("Order cannot be cancelled")

        product_ids = list(map(lambda i: i.product_id, order.items))
        products = {product.id: product for product in (await self.product_crud.get_all(product_ids, for_update=True))}
        for item in order.items:
            products[item.product_id].quantity += item.quantity

        order.status = OrderStatus.CANCELLED

    async def withdraw_order(self, order_id: int):
        order = await self.order_crud.get(order_id)

        # TODO: reconsider order withdrawal behavior for different statuses

        product_ids = list(map(lambda i: i.product_id, order.items))
        products = {product.id: product for product in (await self.product_crud.get_all(product_ids, for_update=True))}
        for item in order.items:
            products[item.product_id].quantity += item.quantity
        return await self.order_crud.delete(order_id)

    async def get_order(self, order_id: int):
        return await self.order_crud.get(order_id)

    async def get_orders(self, filter=None, pagination=None):
        return await self.order_crud.get_all(filter=filter, pagination=pagination)

    async def get_by_user(self, user_id: int):
        return await self.order_crud.get_by_user(user_id)
