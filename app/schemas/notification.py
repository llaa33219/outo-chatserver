from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationOut(BaseModel):
    id: int
    type: str
    payload: dict
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True
