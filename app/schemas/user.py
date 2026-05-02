from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class UserOut(BaseModel):
    id: str
    username: str
    display_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    settings: Optional[dict] = None


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
