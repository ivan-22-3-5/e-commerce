from typing import Literal, Callable, Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.custom_exceptions import ResourceDoesNotExistError
from src.schemas.base import ObjUpdate


class _CRUDBase:
    model = None
    key = None
    not_found_message = None

    @classmethod
    async def _get_one(cls, criteria, db: AsyncSession):
        result = await db.execute(select(cls.model).filter(criteria))
        return result.scalars().first()

    @classmethod
    async def _get_all(cls, criteria, db: AsyncSession):
        result = await db.execute(select(cls.model).filter(criteria))
        return result.scalars().all()

    def __init_subclass__(cls, **kwargs):
        if cls.__base__ is not _CRUDBase:
            if cls.model is None or cls.key is None:
                raise TypeError(f"Class {cls.__name__} must define 'model' and 'key' class attributes.")


class Creatable(_CRUDBase):
    @classmethod
    async def create(cls, obj, db: AsyncSession):
        try:
            db.add(obj)
            await db.flush()
            return obj
        except IntegrityError as e:
            print(e)


class Retrievable(_CRUDBase):
    @classmethod
    async def get(cls, key, db: AsyncSession, *,
                  on_not_found: Literal['raise-error', 'return-none'] = 'raise-error'):
        if (entity := await cls._get_one(cls.key == key, db)) is None and on_not_found == 'raise-error':
            raise ResourceDoesNotExistError(cls.not_found_message or f"Entity with key {key} not found.")
        return entity


class Updatable(_CRUDBase):
    @classmethod
    async def update(cls, key, obj_update: ObjUpdate, db: AsyncSession, *,
                     predicate: Callable[[Any], bool] = None,
                     on_not_found: Literal['raise-error', 'ignore'] = 'raise-error'):
        if (entity_to_update := await cls._get_one(cls.key == key, db)) is None and on_not_found == 'raise-error':
            raise ResourceDoesNotExistError(cls.not_found_message or f"Entity with key {key} not found.")
        if entity_to_update and predicate is None or predicate(entity_to_update):
            for k, v in obj_update.model_dump(exclude_none=True).items():
                setattr(entity_to_update, k, v)


class Deletable(_CRUDBase):
    @classmethod
    async def delete(cls, key, db: AsyncSession, *,
                     predicate: Callable[[Any], bool] = None,
                     on_not_found: Literal['raise-error', 'ignore'] = 'raise-error'):
        if (entity_to_delete := await cls._get_one(cls.key == key, db)) is None and on_not_found == 'raise-error':
            raise ResourceDoesNotExistError(cls.not_found_message or f"Entity with key {key} not found.")
        if entity_to_delete and predicate is None or predicate(entity_to_delete):
            await db.delete(entity_to_delete)
