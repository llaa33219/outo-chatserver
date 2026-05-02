import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Message, Room, User, WorkspaceMember
from app.services.notification_service import create_notification


def _extract_mentions(content: str) -> list[str]:
    return list(set(re.findall(r'@(\w+)', content)))


async def _create_mention_notifications(
    db: AsyncSession,
    message_id: str,
    room_id: str,
    workspace_id: str,
    sender_username: str,
    content: str,
    mentioned_usernames: list[str],
    sender_id: str,
) -> None:
    for username in mentioned_usernames:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        if user is None or user.id == sender_id:
            continue

        is_member = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user.id,
            )
        )
        if is_member.scalar_one_or_none() is None:
            continue

        await create_notification(db, user.id, "mention", {
            "message_id": message_id,
            "room_id": room_id,
            "workspace_id": workspace_id,
            "sender_username": sender_username,
            "content_preview": content[:200],
        })


async def _check_membership(db: AsyncSession, workspace_id: str, user_id: str) -> bool:
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def _check_room_in_workspace(db: AsyncSession, room_id: str, workspace_id: str) -> bool:
    result = await db.execute(
        select(Room).where(Room.id == room_id, Room.workspace_id == workspace_id)
    )
    return result.scalar_one_or_none() is not None


async def get_room_messages(
    db: AsyncSession,
    workspace_id: str,
    room_id: str,
    user_id: str,
    limit: int = 50,
    before: str | None = None,
):
    if not await _check_membership(db, workspace_id, user_id):
        return "not_member"
    if not await _check_room_in_workspace(db, room_id, workspace_id):
        return "room_not_found"

    query = (
        select(Message, User.username)
        .join(User, Message.user_id == User.id)
        .where(Message.room_id == room_id, Message.deleted_at.is_(None))
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    if before:
        sub = await db.execute(select(Message.created_at).where(Message.id == before))
        ts = sub.scalar_one_or_none()
        if ts:
            query = query.where(Message.created_at < ts)

    result = await db.execute(query)
    rows = result.all()

    messages = []
    for msg, username in reversed(rows):
        reply_content = None
        if msg.reply_to_id:
            reply_result = await db.execute(
                select(Message.content).where(Message.id == msg.reply_to_id)
            )
            reply_content = reply_result.scalar_one_or_none()

        messages.append({
            "id": msg.id,
            "room_id": msg.room_id,
            "user_id": msg.user_id,
            "username": username,
            "content": msg.content,
            "reply_to_id": msg.reply_to_id,
            "reply_to_content": reply_content,
            "created_at": msg.created_at,
        })

    return messages


async def send_message(
    db: AsyncSession,
    workspace_id: str,
    room_id: str,
    user_id: str,
    content: str,
):
    if not await _check_membership(db, workspace_id, user_id):
        return "not_member"
    if not await _check_room_in_workspace(db, room_id, workspace_id):
        return "room_not_found"

    msg = Message(room_id=room_id, user_id=user_id, content=content)
    db.add(msg)
    await db.flush()

    result = await db.execute(select(User.username).where(User.id == user_id))
    username = result.scalar_one()

    mentions = _extract_mentions(content)
    if mentions:
        await _create_mention_notifications(
            db, msg.id, room_id, workspace_id, username, content, mentions, user_id
        )

    return {
        "id": msg.id,
        "room_id": msg.room_id,
        "user_id": msg.user_id,
        "username": username,
        "content": msg.content,
        "reply_to_id": msg.reply_to_id,
        "reply_to_content": None,
        "created_at": msg.created_at,
    }


async def reply_to_message(
    db: AsyncSession,
    workspace_id: str,
    room_id: str,
    user_id: str,
    reply_to_id: str,
    content: str,
):
    if not await _check_membership(db, workspace_id, user_id):
        return "not_member"
    if not await _check_room_in_workspace(db, room_id, workspace_id):
        return "room_not_found"

    parent_result = await db.execute(
        select(Message).where(
            Message.id == reply_to_id,
            Message.room_id == room_id,
            Message.deleted_at.is_(None),
        )
    )
    parent_msg = parent_result.scalar_one_or_none()
    if parent_msg is None:
        return "parent_not_found"

    msg = Message(room_id=room_id, user_id=user_id, content=content, reply_to_id=reply_to_id)
    db.add(msg)
    await db.flush()

    result = await db.execute(select(User.username).where(User.id == user_id))
    username = result.scalar_one()

    mentions = _extract_mentions(content)
    if mentions:
        await _create_mention_notifications(
            db, msg.id, room_id, workspace_id, username, content, mentions, user_id
        )

    return {
        "id": msg.id,
        "room_id": msg.room_id,
        "user_id": msg.user_id,
        "username": username,
        "content": msg.content,
        "reply_to_id": msg.reply_to_id,
        "reply_to_content": parent_msg.content,
        "created_at": msg.created_at,
    }
