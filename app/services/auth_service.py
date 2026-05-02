from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.security import hash_password, verify_password, create_access_token
from app.config import get_settings


async def register_user(db: AsyncSession, username: str, password: str) -> User:
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none() is not None:
        raise ValueError("Username already exists")

    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    await db.flush()
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def build_token(user_id: str) -> tuple[str, int]:
    settings = get_settings()
    expires_in = settings.TOKEN_EXPIRE_HOURS * 3600
    token = create_access_token({"sub": user_id})
    return token, expires_in
