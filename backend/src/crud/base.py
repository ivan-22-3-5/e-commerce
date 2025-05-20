import re
from typing import Literal, Callable, Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.custom_exceptions import ResourceDoesNotExistError, ResourceAlreadyExistsError, DependentEntityExistsError
from src.db.db import Base
from src.logger import logger
from src.schemas.base import ObjUpdate
from src.schemas.filtration import PaginationParams


class _CRUDBase:
    model = None
    key = None

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def _get_one(self, criteria):
        result = await self.db.execute(select(self.__class__.model).filter(criteria))
        return result.scalars().first()

    async def _get_all(self,
                       criteria,
                       pagination: PaginationParams = None,
                       order_by=None,
                       for_update: bool = False):
        q = (select(self.__class__.model)
             .filter(criteria)
             .order_by(order_by)
             .limit(pagination and pagination.limit)
             .offset(pagination and pagination.offset))
        result = await self.db.execute(q.with_for_update() if for_update else q)
        return result.scalars().all()

    def __init_subclass__(cls, **kwargs):
        if cls.__base__ is not _CRUDBase:
            if cls.model is None or cls.key is None:
                raise TypeError(f"Class {cls.__name__} must define 'model' and 'key' class attributes.")


class Creatable(_CRUDBase):
    async def create(self, obj):
        try:
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
            return obj
        except IntegrityError as e:
            error_message = str(e.orig)

            if "UniqueViolationError" in error_message:
                raise ResourceAlreadyExistsError(
                    _craft_already_exists_error_message(self.__class__.model, error_message)
                )
            elif "ForeignKeyViolationError" in error_message:
                raise ResourceDoesNotExistError(
                    _craft_doesnt_exist_error_message(self.__class__.model, error_message)
                )
            else:
                logger.error(f"Unexpected IntegrityError: {e}")
                return None


class Retrievable(_CRUDBase):
    async def get(self, key, *, on_not_found: Literal['raise-error', 'return-none'] = 'raise-error'):
        if (entity := await self._get_one(self.__class__.key == key)) is None and on_not_found == 'raise-error':
            raise ResourceDoesNotExistError(
                f"{self.__class__.model.__name__} with the given {str(self.__class__.key).split('.')[-1]} does not exist.")
        return entity


class Updatable(_CRUDBase):

    async def update(self, key, obj_update: ObjUpdate, *,
                     predicate: Callable[[Any], bool] = None,
                     on_not_found: Literal['raise-error', 'ignore'] = 'raise-error'):
        if ((entity_to_update := await self._get_one(self.__class__.key == key)) is None
                and on_not_found == 'raise-error'):
            raise ResourceDoesNotExistError(
                f"{self.__class__.model.__name__} with the given {str(self.__class__.key).split('.')[-1]} does not exist."
            )

        if entity_to_update and predicate is None or predicate(entity_to_update):
            for k, v in obj_update.model_dump(exclude_none=True).items():
                setattr(entity_to_update, k, v)
            await self.db.flush()
            await self.db.refresh(entity_to_update)
            return entity_to_update
        return None


class Deletable(_CRUDBase):
    async def delete(self, key, *,
                     predicate: Callable[[Any], bool] = None,
                     on_not_found: Literal['raise-error', 'ignore'] = 'raise-error'):
        if (
                (entity_to_delete := await self._get_one(self.__class__.key == key)) is None
                and on_not_found == 'raise-error'):
            raise ResourceDoesNotExistError(
                f"{self.__class__.model.__name__} with the given {str(self.__class__.key).split('.')[-1]} does not exist."
            )
        if entity_to_delete and predicate is None or predicate(entity_to_delete):
            try:
                await self.db.delete(entity_to_delete)
                await self.db.flush()
            except IntegrityError as e:
                error_message = str(e.orig)

                if "ForeignKeyViolationError" in error_message:
                    raise DependentEntityExistsError(
                        _craft_dependent_entity_exist_error_message(self.__class__.model, error_message))
                else:
                    logger.error(f"Unexpected IntegrityError: {e}")


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


def _craft_dependent_entity_exist_error_message(model: Base, raw_sql_error_msg: str) -> str:
    err_msg = f"There is some other entity that depends on {model.__name__}"

    if (
            (key_match := re.search(r"Key \((\w+)\)=\((\w+)\)", raw_sql_error_msg))
            and
            (table_match := re.search(r"is still referenced from table \"(\w+)\"", raw_sql_error_msg))
    ):
        err_msg = (f"There is some other entity in relation {table_match.group(1)} "
                   f"that depends on {model.__name__} "
                   f"with the {key_match.group(1)}={key_match.group(2)}")

    return err_msg
