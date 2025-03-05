from src.crud.base import Retrievable, Deletable, Updatable, Creatable
from src.db import models


class ConfirmationTokenCRUD(Creatable, Retrievable, Deletable, Updatable):
    model = models.ConfirmationToken
    key = models.ConfirmationToken.user_id


class RecoveryTokenCRUD(Creatable, Retrievable, Deletable, Updatable):
    model = models.RecoveryToken
    key = models.RecoveryToken.user_id


class RefreshTokenCRUD(Creatable, Retrievable, Deletable, Updatable):
    model = models.RefreshToken
    key = models.RefreshToken.user_id
