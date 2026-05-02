from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Room, WorkspaceMember, Workspace


async def get_workspace_rooms(db: AsyncSession, workspace_id: str, user_id: str):
    membership = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    if membership.scalar_one_or_none() is None:
        return None

    result = await db.execute(
        select(Room).where(Room.workspace_id == workspace_id)
    )
    return result.scalars().all()


async def create_room(db: AsyncSession, workspace_id: str, name: str, user_id: str):
    membership = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    if membership.scalar_one_or_none() is None:
        return None

    room = Room(workspace_id=workspace_id, name=name, created_by=user_id)
    db.add(room)
    await db.flush()
    await db.refresh(room)
    return room


async def delete_room(db: AsyncSession, workspace_id: str, room_id: str, user_id: str):
    workspace = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    ws = workspace.scalar_one_or_none()
    if ws is None or ws.owner_id != user_id:
        return "not_owner"

    room = await db.execute(
        select(Room).where(Room.id == room_id, Room.workspace_id == workspace_id)
    )
    r = room.scalar_one_or_none()
    if r is None:
        return "not_found"

    await db.delete(r)
    await db.flush()
    return r
