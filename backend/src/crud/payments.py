from src.crud import base
from src.db import models


class PaymentCrud(base.Retrievable):
    def __init__(self):
        super().__init__(models.Payment, models.Payment.id)


payments = PaymentCrud()
