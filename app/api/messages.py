from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas.message import (
    MessageCreate,
    MessageOut,
    MessageReply,
    TypingRequest,
    TypingUserOut,
)
from app.services import message_service
from app.services.typing_manager import typing_manager

router = APIRouter(
    prefix="/api/workspaces/{workspace_id}/rooms/{room_id}",
    tags=["messages"],
)


@router.get("/messages", response_model=list[MessageOut])
async def list_messages(
    workspace_id: str,
    room_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    before: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await message_service.get_room_messages(
        db, workspace_id, room_id, current_user.id, limit=limit, before=before
    )
    if result == "not_member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace",
        )
    if result == "room_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    return result


@router.post("/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(
    workspace_id: str,
    room_id: str,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await message_service.send_message(
        db, workspace_id, room_id, current_user.id, body.content
    )
    if result == "not_member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace",
        )
    if result == "room_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    return result


@router.post(
    "/messages/{message_id}/reply",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
async def reply_to_message(
    workspace_id: str,
    room_id: str,
    message_id: str,
    body: MessageReply,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await message_service.reply_to_message(
        db, workspace_id, room_id, current_user.id, message_id, body.content
    )
    if result == "not_member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace",
        )
    if result == "room_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    if result == "parent_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent message not found",
        )
    return result


@router.post("/typing", status_code=status.HTTP_204_NO_CONTENT)
async def set_typing(
    workspace_id: str,
    room_id: str,
    body: TypingRequest,
    current_user: User = Depends(get_current_user),
):
    typing_manager.set_typing(room_id, current_user.id, current_user.username, body.is_typing)


@router.get("/typing", response_model=list[TypingUserOut])
async def get_typing_users(
    workspace_id: str,
    room_id: str,
    current_user: User = Depends(get_current_user),
):
    return typing_manager.get_typing_users(room_id)
