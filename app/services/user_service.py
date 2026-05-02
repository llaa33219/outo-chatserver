from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.schemas.user import SettingsUpdate


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


def get_user_profile(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "created_at": user.created_at,
        "settings": user.settings or {},
    }


async def update_user_settings(
    db: AsyncSession, user: User, settings_update: SettingsUpdate
) -> User:
    if settings_update.display_name is not None:
        user.display_name = settings_update.display_name
    if settings_update.settings is not None:
        user.settings = settings_update.settings
    db.add(user)
    await db.flush()
    return user
