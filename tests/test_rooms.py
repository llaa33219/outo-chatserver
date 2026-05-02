import pytest
from httpx import AsyncClient


async def _create_workspace(client: AsyncClient, headers: dict, name: str = "Test WS") -> str:
    resp = await client.post("/api/workspaces", headers=headers, json={"name": name})
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_room(client: AsyncClient, auth_headers: dict):
    ws_id = await _create_workspace(client, auth_headers)
    resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms",
        headers=auth_headers,
        json={"name": "General"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "General"
    assert data["workspace_id"] == ws_id


@pytest.mark.asyncio
async def test_create_room_not_member(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    ws_id = await _create_workspace(client, auth_headers)
    resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms",
        headers=second_user_headers,
        json={"name": "Unauthorized"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_rooms(client: AsyncClient, auth_headers: dict):
    ws_id = await _create_workspace(client, auth_headers)
    await client.post(f"/api/workspaces/{ws_id}/rooms", headers=auth_headers, json={"name": "Room1"})
    await client.post(f"/api/workspaces/{ws_id}/rooms", headers=auth_headers, json={"name": "Room2"})

    resp = await client.get(f"/api/workspaces/{ws_id}/rooms", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_list_rooms_not_member(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    ws_id = await _create_workspace(client, auth_headers)
    resp = await client.get(f"/api/workspaces/{ws_id}/rooms", headers=second_user_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_room_owner(client: AsyncClient, auth_headers: dict):
    ws_id = await _create_workspace(client, auth_headers)
    room_resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms", headers=auth_headers, json={"name": "To Delete"}
    )
    room_id = room_resp.json()["id"]

    resp = await client.delete(f"/api/workspaces/{ws_id}/rooms/{room_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_room_not_owner(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    ws_id = await _create_workspace(client, auth_headers)
    await client.post(f"/api/workspaces/{ws_id}/join", headers=second_user_headers)

    room_resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms", headers=auth_headers, json={"name": "Protected"}
    )
    room_id = room_resp.json()["id"]

    resp = await client.delete(f"/api/workspaces/{ws_id}/rooms/{room_id}", headers=second_user_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_room_not_found(client: AsyncClient, auth_headers: dict):
    ws_id = await _create_workspace(client, auth_headers)
    resp = await client.delete(f"/api/workspaces/{ws_id}/rooms/nonexistent", headers=auth_headers)
    assert resp.status_code == 404
