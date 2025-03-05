from src.crud.base import Retrievable
from src.db import models


class PaymentCRUD(Retrievable):
    model = models.Payment
    key = models.Payment.id
