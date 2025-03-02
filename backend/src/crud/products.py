from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models
from src.schemas.product import ProductIn, ProductUpdate


async def get_by_id(product_id: int, db: AsyncSession) -> models.Product | None:
    return await base.get_one(select(models.Product).filter(models.Product.id == product_id), db)


async def get_all(*, enabled: bool | None = None, db: AsyncSession) -> list[models.Product] | None:
    query = select(models.Product)
    if enabled is not None:
        query = query.filter(models.Product.enabled == enabled)
    return await base.get_all(query, db)


async def create(product: ProductIn, db: AsyncSession) -> models.Product | None:
    return await base.create(models.Product(
        **product.model_dump()
    ), db)


async def update(product_id: int, product_update: ProductUpdate, db: AsyncSession) -> models.Product | None:
    return await base.update(select(models.Product).filter(models.Product.id == product_id), product_update, db)


async def delete(product_id: int, db: AsyncSession) -> None:
    await base.delete(select(models.Product).filter(models.Product.id == product_id), db)
