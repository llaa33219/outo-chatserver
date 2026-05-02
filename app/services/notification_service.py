from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Notification


async def get_notifications(
    db: AsyncSession, user_id: str, unread_only: bool = False
) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.read == False)
    query = query.order_by(Notification.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def mark_as_read(
    db: AsyncSession, notification_id: int, user_id: str
) -> Notification | None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    notification = result.scalar_one_or_none()
    if notification is None:
        return None
    notification.read = True
    await db.flush()
    await db.refresh(notification)
    return notification


async def create_notification(
    db: AsyncSession, user_id: str, type: str, payload: dict
) -> Notification:
    notification = Notification(user_id=user_id, type=type, payload=payload)
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    return notification
