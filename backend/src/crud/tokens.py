from src.crud.base import Retrievable, Deletable, Updatable
from src.db import models


class ConfirmationTokenCRUD(Retrievable, Deletable, Updatable):
    model = models.ConfirmationToken
    key = models.ConfirmationToken.user_id


class RecoveryTokenCRUD(Retrievable, Deletable, Updatable):
    model = models.RecoveryToken
    key = models.RecoveryToken.user_id


class RefreshTokenCRUD(Retrievable, Deletable, Updatable):
    model = models.RefreshToken
    key = models.RefreshToken.user_id
