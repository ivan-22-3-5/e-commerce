from src.crud import CartItemCRUD
from src.crud.products import ProductCRUD
from src.custom_exceptions import ResourceDoesNotExistError
from src.db.models import CartItem
from src.schemas.cart import Cart
from src.schemas.item import ItemIn, Item


class CartService:
    def __init__(self, cart_item_crud: CartItemCRUD, product_crud: ProductCRUD):
        self.cart_crud = cart_item_crud
        self.product_crud = product_crud

    async def get_cart(self, user_id: int) -> Cart:
        items = await self.cart_crud.get_all_by_user_id(user_id)
        return Cart(
            items=[Item(product_id=item.product_id,
                        quantity=item.quantity,
                        total_price=item.total_price) for item in items],
            total_price=sum(item.total_price for item in items)
        )

    async def add_item(self, user_id: int, item: ItemIn):
        if (await self.product_crud.get(item.product_id)) is None:
            raise ResourceDoesNotExistError("Product with the given id does not exist")

        if existing_item := await self.cart_crud.get(user_id, item.product_id):
            existing_item.quantity += item.quantity
        else:
            await self.cart_crud.create(
                CartItem(
                    user_id=user_id,
                    product_id=item.product_id,
                    quantity=item.quantity)
            )

    async def remove_item(self, user_id: int, item: ItemIn):
        if existing_item := await self.cart_crud.get(user_id, item.product_id):
            if item.quantity >= existing_item.quantity:
                await self.cart_crud.delete(user_id, item.product_id)
            else:
                existing_item.quantity -= item.quantity

    async def clear_cart(self, user_id: int):
        await self.cart_crud.delete_all_by_user_id(user_id)
