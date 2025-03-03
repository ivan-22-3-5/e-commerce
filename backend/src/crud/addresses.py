from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models


class AddressCrud(base.Updatable, base.Deletable):
    def __init__(self):
        super().__init__(models.Address, models.Address.id)

    async def get_by_user(self, user_id: int, db: AsyncSession) -> models.Address | None:
        return await self._get_all(self._model.user_id == user_id, db)


addresses = AddressCrud()
