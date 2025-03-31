from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import _CRUDBase
from src.crud.products import ProductCRUD
from src.custom_exceptions import ResourceDoesNotExistError
from src.db import models
from src.db.models import CartItem
from src.schemas.cart import CartOut
from src.schemas.item import ItemIn, ItemOut


class CartCRUD(_CRUDBase):
    model = models.CartItem

    @classmethod
    async def get_cart(cls, user_id: int, db: AsyncSession) -> CartOut:
        items = await cls._get_all(cls.model.user_id == user_id, db)
        return CartOut(
            items=[ItemOut(product_id=item.product_id,
                           quantity=item.quantity,
                           total_price=item.total_price) for item in items],
            total_price=sum(item.total_price for item in items)
        )

    @classmethod
    async def add_item(cls, user_id: int, item: ItemIn, db: AsyncSession):
        if (await ProductCRUD.get(item.product_id, db)) is None:
            raise ResourceDoesNotExistError("Product with the given id does not exist")

        if existing_item := await cls._get_one(
                and_(cls.model.user_id == user_id, cls.model.product_id == item.product_id), db):
            existing_item.quantity += item.quantity
        else:
            db.add(CartItem(
                user_id=user_id,
                product_id=item.product_id,
                quantity=item.quantity))
        await db.flush()

    @classmethod
    async def remove_item(cls, user_id: int, item: ItemIn, db: AsyncSession):
        if existing_item := await cls._get_one(
                and_(cls.model.user_id == user_id, cls.model.product_id == item.product_id), db):
            if item.quantity >= existing_item.quantity:
                await db.delete(existing_item)
            else:
                existing_item.quantity -= item.quantity
        await db.flush()

    @classmethod
    async def clear(cls, user_id: int, db: AsyncSession):
        items = await cls._get_all(cls.model.user_id == user_id, db)
        for item in items:
            await db.delete(item)
        await db.flush()
