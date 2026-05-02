import json
import re
from collections import defaultdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select
from app.security import decode_access_token
from app.models import User, Message, Room, WorkspaceMember
from app.database import async_session
from app.services.typing_manager import typing_manager
from app.services.notification_service import create_notification

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, room_id: str, ws: WebSocket):
        await ws.accept()
        self._connections[room_id].add(ws)

    def disconnect(self, room_id: str, ws: WebSocket):
        self._connections[room_id].discard(ws)
        if not self._connections[room_id]:
            del self._connections[room_id]

    async def broadcast(self, room_id: str, data: dict, exclude: WebSocket | None = None):
        for ws in list(self._connections.get(room_id, set())):
            if ws != exclude:
                try:
                    await ws.send_json(data)
                except Exception:
                    self.disconnect(room_id, ws)


manager = ConnectionManager()


def _extract_mentions(content: str) -> list[str]:
    return list(set(re.findall(r'@(\w+)', content)))


async def _handle_mentions(db, message_id: str, room_id: str, sender_id: str, sender_username: str, content: str):
    mentions = _extract_mentions(content)
    if not mentions:
        return

    room_result = await db.execute(select(Room.workspace_id).where(Room.id == room_id))
    workspace_id = room_result.scalar_one_or_none()
    if workspace_id is None:
        return

    for username in mentions:
        user_result = await db.execute(select(User).where(User.username == username))
        user = user_result.scalar_one_or_none()
        if user is None or user.id == sender_id:
            continue

        member_result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user.id,
            )
        )
        if member_result.scalar_one_or_none() is None:
            continue

        await create_notification(db, user.id, "mention", {
            "message_id": message_id,
            "room_id": room_id,
            "workspace_id": workspace_id,
            "sender_username": sender_username,
            "content_preview": content[:200],
        })


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(),
):
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = payload.get("sub")
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            await websocket.close(code=4001, reason="User not found")
            return

    username = user.username

    await manager.connect(room_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type")

            if msg_type == "message":
                content = data.get("content", "").strip()
                if not content:
                    continue

                async with async_session() as db:
                    msg = Message(room_id=room_id, user_id=user_id, content=content)
                    db.add(msg)
                    await db.flush()
                    await _handle_mentions(db, msg.id, room_id, user_id, username, content)
                    await db.commit()

                await manager.broadcast(room_id, {
                    "type": "message",
                    "id": msg.id,
                    "room_id": msg.room_id,
                    "user_id": msg.user_id,
                    "username": username,
                    "content": msg.content,
                    "reply_to_id": msg.reply_to_id,
                    "reply_to_content": None,
                    "created_at": msg.created_at.isoformat(),
                })

            elif msg_type == "typing":
                is_typing = data.get("is_typing", False)
                typing_manager.set_typing(room_id, user_id, username, is_typing)
                await manager.broadcast(room_id, {
                    "type": "typing",
                    "user_id": user_id,
                    "username": username,
                    "is_typing": is_typing,
                })

    except WebSocketDisconnect:
        pass
    finally:
        typing_manager.set_typing(room_id, user_id, username, False)
        manager.disconnect(room_id, websocket)
