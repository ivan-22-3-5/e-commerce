from typing import Type

from src.crud import base
from src.db import models


class TokenCrud(base.Deletable, base.Updatable):
    def __init__(self, model: Type[models.TokenBase]):
        super().__init__(model, model.user_id)


confirmation_tokens = TokenCrud(models.ConfirmationToken)
recovery_tokens = TokenCrud(models.RecoveryToken)
refresh_tokens = TokenCrud(models.RefreshToken)
