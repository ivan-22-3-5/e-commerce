from pydantic import BaseModel, field_validator, Field

from src.utils import hash_pass


class NewPasswordIn(BaseModel):
    token: str
    password: str = Field(min_length=5)

    @field_validator('password', mode='after')
    @classmethod
    def hash_password(cls, password) -> str:
        return hash_pass(password)

