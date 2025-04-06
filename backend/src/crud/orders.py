from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Creatable
from src.db import models


class OrderCRUD(Creatable, Retrievable):
    model = models.Order
    key = models.Order.id

    @classmethod
    async def get_by_user(cls, user_id: int, db: AsyncSession) -> list[models.Order] | None:
        return await cls._get_all(cls.model.user_id == user_id, db)
