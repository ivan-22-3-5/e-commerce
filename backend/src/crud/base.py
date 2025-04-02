import re
from typing import Literal, Callable, Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.custom_exceptions import ResourceDoesNotExistError, ResourceAlreadyExistsError
from src.db.db import Base
from src.logger import logger
from src.schemas.base import ObjUpdate
from src.schemas.filtration import PaginationParams


class _CRUDBase:
    model = None
    key = None
    not_found_message = None

    @classmethod
    async def _get_one(cls, criteria, db: AsyncSession):
        result = await db.execute(select(cls.model).filter(criteria))
        return result.scalars().first()

    @classmethod
    async def _get_all(cls, criteria, db: AsyncSession, pagination: PaginationParams = None, order_by=None):
        result = await db.execute(select(cls.model).filter(criteria).order_by(order_by)
                                  .limit(pagination and pagination.limit).offset(pagination and pagination.offset))
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
            await db.refresh(obj)
            return obj
        except IntegrityError as e:
            error_message = str(e.orig)

            if "UniqueViolationError" in error_message:
                raise ResourceAlreadyExistsError(_craft_already_exists_error_message(cls.model, error_message))
            elif "ForeignKeyViolationError" in error_message:
                raise ResourceDoesNotExistError(_craft_doesnt_exist_error_message(cls.model, error_message))
            else:
                logger.error(f"Unexpected IntegrityError: {e}")


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
            await db.flush()
            await db.refresh(entity_to_update)
            return entity_to_update


class Deletable(_CRUDBase):
    @classmethod
    async def delete(cls, key, db: AsyncSession, *,
                     predicate: Callable[[Any], bool] = None,
                     on_not_found: Literal['raise-error', 'ignore'] = 'raise-error'):
        if (entity_to_delete := await cls._get_one(cls.key == key, db)) is None and on_not_found == 'raise-error':
            raise ResourceDoesNotExistError(cls.not_found_message or f"Entity with key {key} not found.")
        if entity_to_delete and predicate is None or predicate(entity_to_delete):
            await db.delete(entity_to_delete)


def _craft_already_exists_error_message(model: Base, raw_sql_error_msg: str) -> str:
    err_msg = f"{model.__name__} with the given attributes already exists"

    if match := re.search(r"Key \((\w+)\)", raw_sql_error_msg):
        err_msg = f"{model.__name__} with the given {match.group(1)} already exists"

    return err_msg


def _craft_doesnt_exist_error_message(model: Base, raw_sql_error_msg: str) -> str:
    err_msg = f"Some entity {model.__name__} depends on does not exists"

    if (
            (key_match := re.search(r"Key \((\w+)\)=\((\w+)\)", raw_sql_error_msg))
            and
            (table_match := re.search(r"not present in table \"(\w+)\"", raw_sql_error_msg))
    ):
        err_msg = f"There are no {table_match.group(1)} with the {key_match.group(1)}={key_match.group(2)}"

    return err_msg
