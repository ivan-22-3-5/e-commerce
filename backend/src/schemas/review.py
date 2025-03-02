from datetime import datetime

from pydantic import BaseModel, Field


class ReviewIn(BaseModel):
    rating: int = Field(le=10, ge=0)
    content: str = Field(max_length=1024)


class ReviewOut(BaseModel):
    id: int
    user_id: int
    rating: int
    content: str
    created_at: datetime
