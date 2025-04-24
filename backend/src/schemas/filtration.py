from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.custom_types import OrderStatus


class PaginationParams(BaseModel):
    limit: int = Field(50, gt=0, le=100)
    offset: int = Field(0, ge=0)


class OrderFilter(BaseModel):
    status: Optional[OrderStatus] = Field(None)
    created_after: Optional[datetime] = Field(None)
