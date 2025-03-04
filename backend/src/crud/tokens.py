from src.crud.base import Retrievable, Deletable, Updatable
from src.db import models


class ConfirmationTokenCrud(Retrievable, Deletable, Updatable):
    model = models.ConfirmationToken
    key = models.ConfirmationToken.user_id


class RecoveryTokenCrud(Retrievable, Deletable, Updatable):
    model = models.RecoveryToken
    key = models.RecoveryToken.user_id


class RefreshTokenCrud(Retrievable, Deletable, Updatable):
    model = models.RefreshToken
    key = models.RefreshToken.user_id
