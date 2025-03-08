from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Creatable
from src.crud.products import ProductCRUD
from src.db import models
from src.schemas.item import ItemIn


class CartCRUD(Creatable, Retrievable):
    model = models.Cart
    key = models.Cart.user_id

    @classmethod
    async def add_item(cls, user_id: int, item: ItemIn, db: AsyncSession) -> models.Cart | None:
        cart = await cls.get(user_id, db)
        if cart and await ProductCRUD.get(item.product_id, db):
            cart.add_item(**item.model_dump())
            return cart

    @classmethod
    async def remove_item(cls, user_id: int, item: ItemIn, db: AsyncSession) -> models.Cart | None:
        cart = await cls.get(user_id, db)
        if cart:
            cart.remove_item(**item.model_dump())
            return cart

    @classmethod
    async def clear(cls, user_id: int, db: AsyncSession) -> models.Cart | None:
        cart = await cls.get(user_id, db)
        if cart:
            cart.clear()
            return cart
