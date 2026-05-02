from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/chat.db"
    SECRET_KEY: str = "change-me-to-a-random-secret-key-min-32-chars"
    TOKEN_EXPIRE_HOURS: int = 24
    ENCRYPTION_KEY: str = ""
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
