from sqlalchemy import and_, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Updatable, Deletable, Creatable
from src.db import models
from src.logger import logger
from src.schemas.filtration import PaginationParams


class ProductCRUD(Creatable, Retrievable, Updatable, Deletable):
    model = models.Product
    key = models.Product.id

    @classmethod
    async def get_all(cls, ids: list[int] = None, *,
                      pagination: PaginationParams = None,
                      is_active: bool | None = None,
                      order_by=None,
                      for_update=False,
                      db: AsyncSession) -> list[models.Product] | None:
        return await cls._get_all(and_(
            models.Product.id.in_(ids) if ids is not None else True,
            models.Product.is_active == is_active if is_active is not None else True
        ), db, pagination=pagination, order_by=order_by or cls.key, for_update=for_update)

    @classmethod
    async def search(cls, query: str, db: AsyncSession) -> list[models.Product]:
        ts_query = func.plainto_tsquery('english', query)
        logger.info(f"ts_query: {ts_query}")
        tsvector = func.to_tsvector('english', models.Product.title + ' ' + models.Product.description)

        stmt = select(models.Product).where(
            tsvector.op('@@')(ts_query)
        ).order_by(desc(func.ts_rank(tsvector, ts_query)))

        result = await db.execute(stmt)
        return result.scalars().all()
