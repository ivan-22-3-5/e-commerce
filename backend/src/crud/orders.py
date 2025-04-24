from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Creatable
from src.db import models
from src.schemas.filtration import PaginationParams, OrderFilter


class OrderCRUD(Creatable, Retrievable):
    model = models.Order
    key = models.Order.id

    @classmethod
    async def get_by_user(cls, user_id: int, db: AsyncSession) -> list[models.Order] | None:
        return await cls._get_all(cls.model.user_id == user_id, db)

    @classmethod
    async def get_all(cls,
                      db: AsyncSession,
                      pagination: PaginationParams = None,
                      filter: OrderFilter = None) -> list[models.Order] | None:
        return await cls._get_all(
            and_(
                (cls.model.status == filter.status) if filter.status is not None else True,
                (cls.model.created_at >= filter.created_after) if filter.created_after is not None else True
            ) if filter is not None else True,
            order_by=cls.model.created_at,
            pagination=pagination,
            db=db,
        )
