from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from app.models import Friendship, User


async def get_friends(db: AsyncSession, user_id: str) -> list[Friendship]:
    result = await db.execute(
        select(Friendship)
        .where(
            or_(
                Friendship.user_id == user_id,
                Friendship.friend_id == user_id,
            ),
            Friendship.status == "accepted",
        )
        .options(selectinload(Friendship.user), selectinload(Friendship.friend))
    )
    return list(result.scalars().all())


async def add_friend(db: AsyncSession, user_id: str, friend_id: str) -> Friendship:
    result = await db.execute(select(User).where(User.id == friend_id))
    if result.scalar_one_or_none() is None:
        raise ValueError("User not found")

    existing = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == user_id),
            )
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError("Friendship already exists")

    friendship = Friendship(user_id=user_id, friend_id=friend_id, status="accepted")
    db.add(friendship)
    await db.flush()

    result = await db.execute(
        select(Friendship)
        .where(Friendship.id == friendship.id)
        .options(selectinload(Friendship.user), selectinload(Friendship.friend))
    )
    return result.scalar_one()


async def remove_friend(db: AsyncSession, user_id: str, friend_id: str) -> None:
    result = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == user_id),
            )
        )
    )
    friendship = result.scalar_one_or_none()
    if friendship is None:
        raise ValueError("Friendship not found")

    await db.delete(friendship)
    await db.flush()
