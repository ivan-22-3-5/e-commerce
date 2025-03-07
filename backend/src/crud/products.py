from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Updatable, Deletable, Creatable
from src.db import models


class ProductCRUD(Creatable, Retrievable, Updatable, Deletable):
    model = models.Product
    key = models.Product.id
    not_found_message = "Product with the given id does not exist"

    @classmethod
    async def get_all(cls, ids: list[int] = None, *,
                      enabled: bool | None = None, db: AsyncSession) -> list[models.Product] | None:
        # TODO: rewrite condition
        return await cls._get_all(and_(
            models.Product.id.in_(ids) if ids is not None else True,
            models.Product.enabled == enabled if enabled is not None else True
        ), db)
