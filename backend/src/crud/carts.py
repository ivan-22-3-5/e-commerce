from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base, products
from src.db import models
from src.schemas.item import ItemIn


class CartCrud(base.Retrievable):
    def __init__(self):
        super().__init__(models.Cart, models.Cart.user_id)

    async def add_item(self, user_id: int, item: ItemIn, db: AsyncSession) -> models.Cart | None:
        cart = await self.get_one(user_id, db)
        if cart and await products.get_by_id(item.product_id, db):
            cart.add_item(**item.model_dump())
            await db.commit()
            await db.refresh(cart)
            return cart

    async def remove_item(self, user_id: int, item: ItemIn, db: AsyncSession) -> models.Cart | None:
        cart = await self.get_one(user_id, db)
        if cart:
            cart.remove_item(**item.model_dump())
            await db.commit()
            await db.refresh(cart)
            return cart

    async def clear(self, user_id: int, db: AsyncSession) -> models.Cart | None:
        cart = await self.get_one(user_id, db)
        if cart:
            cart.clear()
            await db.commit()
            await db.refresh(cart)
            return cart
