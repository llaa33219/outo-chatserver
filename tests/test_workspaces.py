import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_workspace(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/workspaces", headers=auth_headers, json={"name": "Test Workspace"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Workspace"
    assert data["member_count"] == 1
    assert "id" in data
    assert "owner_id" in data


@pytest.mark.asyncio
async def test_list_workspaces(client: AsyncClient, auth_headers: dict):
    await client.post("/api/workspaces", headers=auth_headers, json={"name": "WS1"})
    await client.post("/api/workspaces", headers=auth_headers, json={"name": "WS2"})

    resp = await client.get("/api/workspaces", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_join_workspace(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    create_resp = await client.post(
        "/api/workspaces", headers=auth_headers, json={"name": "Joinable"}
    )
    ws_id = create_resp.json()["id"]

    resp = await client.post(f"/api/workspaces/{ws_id}/join", headers=second_user_headers)
    assert resp.status_code == 200
    assert resp.json()["member_count"] == 2


@pytest.mark.asyncio
async def test_join_workspace_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/workspaces/nonexistent/join", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_workspace_members(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    create_resp = await client.post(
        "/api/workspaces", headers=auth_headers, json={"name": "Members WS"}
    )
    ws_id = create_resp.json()["id"]

    await client.post(f"/api/workspaces/{ws_id}/join", headers=second_user_headers)
    resp = await client.get(f"/api/workspaces/{ws_id}/members", headers=auth_headers)
    assert resp.status_code == 200
    members = resp.json()
    assert len(members) == 2


@pytest.mark.asyncio
async def test_delete_workspace_owner(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/workspaces", headers=auth_headers, json={"name": "To Delete"}
    )
    ws_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/workspaces/{ws_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_workspace_not_owner(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    create_resp = await client.post(
        "/api/workspaces", headers=auth_headers, json={"name": "Not Owner"}
    )
    ws_id = create_resp.json()["id"]

    await client.post(f"/api/workspaces/{ws_id}/join", headers=second_user_headers)
    resp = await client.delete(f"/api/workspaces/{ws_id}", headers=second_user_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_workspace_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/workspaces/nonexistent", headers=auth_headers)
    assert resp.status_code == 404
