from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models import Workspace, WorkspaceMember, User


async def get_user_workspaces(db: AsyncSession, user_id: str) -> list[Workspace]:
    result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user_id)
        .options(selectinload(Workspace.members))
    )
    return list(result.scalars().all())


async def create_workspace(db: AsyncSession, name: str, owner_id: str) -> Workspace:
    workspace = Workspace(name=name, owner_id=owner_id)
    db.add(workspace)
    await db.flush()

    membership = WorkspaceMember(workspace_id=workspace.id, user_id=owner_id)
    db.add(membership)
    await db.flush()

    result = await db.execute(
        select(Workspace)
        .where(Workspace.id == workspace.id)
        .options(selectinload(Workspace.members))
    )
    return result.scalar_one()


async def join_workspace(db: AsyncSession, workspace_id: str, user_id: str) -> Workspace:
    result = await db.execute(
        select(Workspace)
        .where(Workspace.id == workspace_id)
        .options(selectinload(Workspace.members))
    )
    workspace = result.scalar_one_or_none()
    if workspace is None:
        return None

    existing = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return workspace

    membership = WorkspaceMember(workspace_id=workspace_id, user_id=user_id)
    db.add(membership)
    await db.flush()

    await db.refresh(workspace, ["members"])
    return workspace


async def get_workspace_members(db: AsyncSession, workspace_id: str) -> list[dict]:
    result = await db.execute(
        select(WorkspaceMember, User)
        .join(User, WorkspaceMember.user_id == User.id)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    rows = result.all()
    return [
        {
            "user_id": member.user_id,
            "username": user.username,
            "display_name": user.display_name,
            "joined_at": member.joined_at,
        }
        for member, user in rows
    ]


async def delete_workspace(db: AsyncSession, workspace_id: str, user_id: str) -> bool:
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if workspace is None:
        return False
    if workspace.owner_id != user_id:
        return False

    await db.delete(workspace)
    await db.flush()
    return True
