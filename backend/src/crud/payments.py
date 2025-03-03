from src.crud import base
from src.db import models


class PaymentCRUD(base.Retrievable):
    def __init__(self):
        super().__init__(models.Payment, models.Payment.id)
