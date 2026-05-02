import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/register", json={"username": "newuser", "password": "password123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    await client.post("/api/register", json={"username": "dupuser", "password": "password123"})
    resp = await client.post("/api/register", json={"username": "dupuser", "password": "password123"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Username already exists"


@pytest.mark.asyncio
async def test_register_short_username(client: AsyncClient):
    resp = await client.post("/api/register", json={"username": "ab", "password": "password123"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    resp = await client.post("/api/register", json={"username": "validuser", "password": "short"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/register", json={"username": "loginuser", "password": "password123"})
    resp = await client.post("/api/token", json={"username": "loginuser", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/register", json={"username": "wrongpw", "password": "password123"})
    resp = await client.post("/api/token", json={"username": "wrongpw", "password": "wrongpassword"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post("/api/token", json={"username": "nouser", "password": "password123"})
    assert resp.status_code == 401
