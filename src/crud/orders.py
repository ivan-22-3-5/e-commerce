from sqlalchemy import and_

from src.crud.base import Retrievable, Creatable, Deletable
from src.db import models
from src.schemas.filtration import PaginationParams, OrderFilter


class OrderCRUD(Creatable, Retrievable, Deletable):
    model = models.Order
    key = models.Order.id

    async def get_by_user(self, user_id: int) -> list[models.Order] | None:
        return await self._get_all(self.__class__.model.user_id == user_id)

    async def get_all(self,
                      pagination: PaginationParams = None,
                      filter: OrderFilter = None) -> list[models.Order] | None:
        return await self._get_all(
            and_(
                (self.__class__.model.status == filter.status) if filter.status is not None else True,
                (self.__class__.model.created_at >= filter.created_after) if filter.created_after is not None else True
            ) if filter is not None else True,
            order_by=self.__class__.model.created_at,
            pagination=pagination,
        )
