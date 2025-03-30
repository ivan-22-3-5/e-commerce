from pydantic import BaseModel, EmailStr, field_validator, Field

from src.config import rules
from src.utils import hash_pass


class UserIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=rules.MIN_PASSWORD_LENGTH)
    name: str = Field(min_length=rules.MIN_USERNAME_LENGTH, max_length=rules.MAX_USERNAME_LENGTH)
    confirmation_code: int = Field(ge=rules.CONFIRMATION_CODE_LOWER_BOUND,
                                   le=rules.CONFIRMATION_CODE_UPPER_BOUND)

    @field_validator('password', mode='after')
    @classmethod
    def hash_password(cls, password) -> str:
        return hash_pass(password)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str


class GoogleUserInfo(BaseModel):
    id: str = Field(validation_alias="sub")
    name: str
    email: str
    email_verified: bool
