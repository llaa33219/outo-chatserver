from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceOut, WorkspaceMemberOut
from app.services import workspace_service

router = APIRouter(prefix="/api", tags=["workspaces"])


@router.get("/workspaces", response_model=list[WorkspaceOut])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspaces = await workspace_service.get_user_workspaces(db, current_user.id)
    return [
        WorkspaceOut(
            id=w.id,
            name=w.name,
            owner_id=w.owner_id,
            member_count=len(w.members),
            created_at=w.created_at,
        )
        for w in workspaces
    ]


@router.post("/workspaces", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    body: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = await workspace_service.create_workspace(db, body.name, current_user.id)
    return WorkspaceOut(
        id=workspace.id,
        name=workspace.name,
        owner_id=workspace.owner_id,
        member_count=len(workspace.members),
        created_at=workspace.created_at,
    )


@router.post("/workspaces/{workspace_id}/join", response_model=WorkspaceOut)
async def join_workspace(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = await workspace_service.join_workspace(db, workspace_id, current_user.id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return WorkspaceOut(
        id=workspace.id,
        name=workspace.name,
        owner_id=workspace.owner_id,
        member_count=len(workspace.members),
        created_at=workspace.created_at,
    )


@router.get("/workspaces/{workspace_id}/members", response_model=list[WorkspaceMemberOut])
async def list_workspace_members(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    members = await workspace_service.get_workspace_members(db, workspace_id)
    return members


@router.delete("/workspaces/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await workspace_service.delete_workspace(db, workspace_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or you are not the owner",
        )
