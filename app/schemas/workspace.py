from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class WorkspaceOut(BaseModel):
    id: str
    name: str
    owner_id: str
    member_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceMemberOut(BaseModel):
    user_id: str
    username: str
    display_name: Optional[str]
    joined_at: datetime
