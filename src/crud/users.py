from src.crud.base import Retrievable, Creatable
from src.db import models


class UserCRUD(Creatable, Retrievable):
    model = models.User
    key = models.User.id

    async def get_by_email(self, email: str) -> models.User | None:
        return await self._get_one(models.User.email == email)

    async def get_by_idp_id(self, idp_id: str) -> models.User | None:
        return await self._get_one(models.User.identity_provider_id == idp_id)
