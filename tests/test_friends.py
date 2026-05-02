import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_friends_empty(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/friends", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_add_friend(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    profile = await client.get("/api/me", headers=second_user_headers)
    friend_id = profile.json()["id"]

    resp = await client.post("/api/friends", headers=auth_headers, json={"friend_id": friend_id})
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "seconduser"
    assert data["status"] == "accepted"


@pytest.mark.asyncio
async def test_add_friend_self(client: AsyncClient, auth_headers: dict):
    profile = await client.get("/api/me", headers=auth_headers)
    my_id = profile.json()["id"]

    resp = await client.post("/api/friends", headers=auth_headers, json={"friend_id": my_id})
    assert resp.status_code == 400
    assert "yourself" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_add_friend_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/friends",
        headers=auth_headers,
        json={"friend_id": "nonexistent-id"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_friend_duplicate(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    profile = await client.get("/api/me", headers=second_user_headers)
    friend_id = profile.json()["id"]

    await client.post("/api/friends", headers=auth_headers, json={"friend_id": friend_id})
    resp = await client.post("/api/friends", headers=auth_headers, json={"friend_id": friend_id})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_remove_friend(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    profile = await client.get("/api/me", headers=second_user_headers)
    friend_id = profile.json()["id"]

    await client.post("/api/friends", headers=auth_headers, json={"friend_id": friend_id})
    resp = await client.delete(f"/api/friends/{friend_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_remove_friend_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/friends/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_friends_after_add(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    profile = await client.get("/api/me", headers=second_user_headers)
    friend_id = profile.json()["id"]

    await client.post("/api/friends", headers=auth_headers, json={"friend_id": friend_id})
    resp = await client.get("/api/friends", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["username"] == "seconduser"
