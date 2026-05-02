from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.user import UserOut, SettingsUpdate
from app.services.user_service import get_user_profile, update_user_settings

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/me", response_model=UserOut)
async def read_current_user(user: User = Depends(get_current_user)):
    return get_user_profile(user)


@router.put("/me/settings", response_model=UserOut)
async def update_settings(
    settings_update: SettingsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated = await update_user_settings(db, user, settings_update)
    return get_user_profile(updated)
