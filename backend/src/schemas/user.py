from pydantic import BaseModel, EmailStr, field_validator, Field

from src.utils import hash_pass


class UserIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=5)
    username: str = Field(min_length=3, max_length=32)

    @field_validator('password', mode='after')
    @classmethod
    def hash_password(cls, password) -> str:
        return hash_pass(password)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
