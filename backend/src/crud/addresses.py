from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Updatable, Deletable, Creatable
from src.db import models


class AddressCRUD(Creatable, Retrievable, Updatable, Deletable):
    model = models.Address
    key = models.Address.id
    not_found_message = "Address with the given id does not exist"

    @classmethod
    async def get_by_user(cls, user_id: int, db: AsyncSession) -> models.Address | None:
        return await cls._get_all(cls.model.user_id == user_id, db)
