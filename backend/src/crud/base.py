from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.base import ObjUpdate


class CrudBase:
    def __init__(self, model, key):
        self._model = model
        self._key = key


class Retrievable(CrudBase):
    async def get_one(self, key, db: AsyncSession):
        result = await db.execute(select(self._model).filter(self._key == key))
        return result.scalars().first()

    async def get_all(self, key, db: AsyncSession):
        result = await db.execute(select(self._model).filter(self._key == key))
        return result.scalars().all()

    async def _get_one(self, criteria, db: AsyncSession):
        result = await db.execute(select(self._model).filter(criteria))
        return result.scalars().first()

    async def _get_all(self, criteria, db: AsyncSession):
        result = await db.execute(select(self._model).filter(criteria))
        return result.scalars().all()


class Updatable(Retrievable):
    async def update(self, key, obj_update: ObjUpdate, db: AsyncSession):
        obj_to_update = await self.get_one(key, db)
        if obj_to_update:
            for k, v in obj_update.model_dump(exclude_none=True).items():
                setattr(obj_to_update, k, v)


class Deletable(Retrievable):
    async def delete(self, key, db: AsyncSession):
        obj_to_delete = await self.get_one(key, db)
        if obj_to_delete:
            await db.delete(obj_to_delete)
