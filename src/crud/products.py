from sqlalchemy import and_, func, desc, select

from src.crud.base import Retrievable, Updatable, Deletable, Creatable
from src.db import models
from src.db.models import product_category_association
from src.schemas.filtration import PaginationParams


class ProductCRUD(Creatable, Retrievable, Updatable, Deletable):
    model = models.Product
    key = models.Product.id

    async def get_all(self, ids: list[int] = None, *,
                      pagination: PaginationParams = None,
                      is_active: bool | None = None,
                      order_by=None,
                      for_update=False) -> list[models.Product] | None:
        return await self._get_all(and_(
            models.Product.id.in_(ids) if ids is not None else True,
            models.Product.is_active == is_active if is_active is not None else True
        ), pagination=pagination, order_by=order_by or self.__class__.key, for_update=for_update)

    async def search(self, query: str, *,
                     category_ids: list[int] | None = None,
                     pagination: PaginationParams = None) -> list[models.Product]:
        ts_query = func.plainto_tsquery('english', query)
        tsvector = func.to_tsvector('english', models.Product.title + ' ' + models.Product.description)
        rank = func.ts_rank(tsvector, ts_query)

        stmt = select(models.Product, rank).distinct()

        if category_ids:
            assoc = product_category_association

            stmt = stmt.join(assoc, models.Product.id == assoc.c.product_id)
            stmt = stmt.where(assoc.c.category_id.in_(category_ids))

        stmt = stmt.where(and_(tsvector.op('@@')(ts_query),
                               models.Product.is_active == True))
        stmt = stmt.limit(pagination and pagination.limit).offset(pagination and pagination.offset)
        stmt = stmt.order_by(desc(rank))

        result = await self.db.execute(stmt)
        return list(map(lambda x: x[0], result.all()))
