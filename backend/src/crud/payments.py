from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models
from src.schemas.payment import PaymentIn


async def get_by_id(payment_id: int, db: AsyncSession) -> models.Payment | None:
    return await base.get_one(select(models.Payment).filter(models.Payment.id == payment_id), db)


async def create(payment: PaymentIn, db: AsyncSession) -> models.Payment:
    return await base.create(models.Payment(
        **payment.model_dump()), db)
