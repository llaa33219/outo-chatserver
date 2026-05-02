import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client: AsyncClient):
    resp = await client.get("/api/me")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_update_settings(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/me/settings",
        headers=auth_headers,
        json={"display_name": "Test User", "settings": {"theme": "dark"}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Test User"


@pytest.mark.asyncio
async def test_update_settings_partial(client: AsyncClient, auth_headers: dict):
    await client.put(
        "/api/me/settings",
        headers=auth_headers,
        json={"display_name": "Original"},
    )
    resp = await client.put(
        "/api/me/settings",
        headers=auth_headers,
        json={"display_name": "Updated"},
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Updated"
