from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models import User, Friendship
from app.schemas.friend import FriendAdd, FriendOut
from app.services import friend_service

router = APIRouter(prefix="/api", tags=["friends"])


def _friendship_to_out(friendship: Friendship, current_user_id: str) -> FriendOut:
    if friendship.user_id == current_user_id:
        friend_user = friendship.friend
    else:
        friend_user = friendship.user
    return FriendOut(
        id=friend_user.id,
        username=friend_user.username,
        display_name=friend_user.display_name,
        status=friendship.status,
        since=friendship.created_at,
    )


@router.get("/friends", response_model=list[FriendOut])
async def list_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    friendships = await friend_service.get_friends(db, current_user.id)
    return [_friendship_to_out(f, current_user.id) for f in friendships]


@router.post("/friends", response_model=FriendOut, status_code=201)
async def add_friend(
    data: FriendAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")

    try:
        friendship = await friend_service.add_friend(db, current_user.id, data.friend_id)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "already exists" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

    return _friendship_to_out(friendship, current_user.id)


@router.delete("/friends/{friend_id}", status_code=204)
async def remove_friend(
    friend_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await friend_service.remove_friend(db, current_user.id, friend_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Friendship not found")
