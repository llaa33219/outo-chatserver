from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class RoomOut(BaseModel):
    id: str
    workspace_id: str
    name: str
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True
