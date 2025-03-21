from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    limit: int = Field(50, gt=0, le=100)
    offset: int = Field(0, ge=0)
