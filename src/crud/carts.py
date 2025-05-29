from sqlalchemy import and_

from src.crud.base import Creatable
from src.db import models
from src.db.models import CartItem


class CartItemCRUD(Creatable):
    model = models.CartItem
    key = models.CartItem.user_id

    async def get(self, user_id: int, product_id: int) -> CartItem | None:
        return await self._get_one(and_(self.__class__.model.user_id == user_id,
                                        self.__class__.model.product_id == product_id))

    async def get_all_by_user_id(self, user_id: int) -> list[CartItem]:
        return await self._get_all(self.__class__.model.user_id == user_id)

    async def delete_all_by_user_id(self, user_id: int):
        items = await self._get_all(self.__class__.model.user_id == user_id)
        for item in items:
            await self.db.delete(item)
        await self.db.flush()

    async def delete(self, user_id: int, product_id: int):
        item = await self.get(user_id, product_id)
        if item:
            await self.db.delete(item)
            await self.db.flush()
