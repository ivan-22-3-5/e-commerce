from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.custom_types import OrderStatus
from src.db import models
from src.schemas.order import OrderIn


async def get_by_id(order_id: int, db: AsyncSession) -> models.Order | None:
    return await base.get_one(select(models.Order).filter(models.Order.id == order_id), db)


async def get_by_user(user_id: int, db: AsyncSession) -> list[models.Order] | None:
    return await base.get_all(select(models.Order).filter(models.Order.user_id == user_id), db)


async def create(order: OrderIn, user_id: int, db: AsyncSession) -> models.Order | None:
    return await base.create(models.Order(
        user_id=user_id,
        **order.model_dump()
    ), db)


async def update_status(order_id: int, new_status: OrderStatus, db: AsyncSession):
    await base.update_property(select(models.Order).filter(models.Order.id == order_id),
                               'status', new_status, db)


async def pay_order(order_id: int, db: AsyncSession):
    await base.update_property(select(models.Order).filter(models.Order.id == order_id),
                               'is_paid', True, db)

