from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)


class MessageReply(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)


class MessageOut(BaseModel):
    id: str
    room_id: str
    user_id: str
    username: str
    content: str
    reply_to_id: Optional[str]
    reply_to_content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TypingRequest(BaseModel):
    is_typing: bool


class TypingUserOut(BaseModel):
    user_id: str
    username: str
