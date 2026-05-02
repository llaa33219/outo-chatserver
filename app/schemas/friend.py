from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FriendAdd(BaseModel):
    friend_id: str


class FriendOut(BaseModel):
    id: str
    username: str
    display_name: Optional[str]
    status: str
    since: datetime

    class Config:
        from_attributes = True
