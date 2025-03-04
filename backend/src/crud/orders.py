from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable
from src.custom_types import OrderStatus
from src.db import models


class OrderCrud(Retrievable):
    model = models.Order
    key = models.Order.id

    @classmethod
    async def get_by_user(cls, user_id: int, db: AsyncSession) -> list[models.Order] | None:
        return await cls._get_all(cls.model.user_id == user_id, db)

    @classmethod
    async def update_status(cls, order_id: int, new_status: OrderStatus, db: AsyncSession):
        order = await cls.get_one(order_id, db)
        order.status = new_status

    @classmethod
    async def pay_order(cls, order_id: int, db: AsyncSession):
        order = await cls.get_one(order_id, db)
        order.is_paid = True
