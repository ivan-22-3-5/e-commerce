from src.crud.base import Retrievable, Creatable
from src.db import models


class PaymentCRUD(Creatable, Retrievable):
    model = models.Payment
    key = models.Payment.id
