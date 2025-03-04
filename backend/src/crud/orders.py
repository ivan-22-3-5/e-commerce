from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.custom_types import OrderStatus
from src.db import models


class OrderCrud(base.Retrievable):
    def __init__(self):
        super().__init__(models.Order, models.Order.id)

    async def get_by_user(self, user_id: int, db: AsyncSession) -> list[models.Order] | None:
        return await self._get_all(self._model.user_id == user_id, db)

    async def update_status(self, order_id: int, new_status: OrderStatus, db: AsyncSession):
        order = await self.get_one(order_id, db)
        order.status = new_status

    async def pay_order(self, order_id: int, db: AsyncSession):
        order = await self.get_one(order_id, db)
        order.is_paid = True


orders = OrderCrud()
