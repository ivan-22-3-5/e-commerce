from src.crud.base import Deletable, Creatable
from src.db import models
from src.db.models import CartItem


class CartItemCRUD(Deletable, Creatable):
    model = models.CartItem
    key = models.CartItem.user_id

    async def get_all_by_user_id(self, user_id: int) -> list[CartItem]:
        return await self._get_all(self.__class__.model.user_id == user_id)

    async def delete_all_by_user_id(self, user_id: int):
        items = await self._get_all(self.__class__.model.user_id == user_id)
        for item in items:
            await self.db.delete(item)
        await self.db.flush()
