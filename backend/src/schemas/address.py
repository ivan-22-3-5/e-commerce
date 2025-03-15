from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.base import ObjUpdate


class AddressIn(BaseModel):
    fullname: str = Field(max_length=32)
    country: str = Field(max_length=32)
    city: str = Field(max_length=64)
    street: str = Field(max_length=64)
    zipcode: str = Field(max_length=10)


class AddressOut(BaseModel):
    id: int
    fullname: str
    country: str
    city: str
    street: str
    zipcode: str


class AddressUpdate(ObjUpdate):
    fullname: Optional[str] = Field(default=None, max_length=32)
    country: Optional[str] = Field(default=None, max_length=32)
    city: Optional[str] = Field(default=None, max_length=64)
    street: Optional[str] = Field(default=None, max_length=64)
    zipcode: Optional[str] = Field(default=None, max_length=10)
