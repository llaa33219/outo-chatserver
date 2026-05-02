import pytest
from httpx import AsyncClient


async def _setup_workspace_and_room(client: AsyncClient, headers: dict) -> tuple[str, str]:
    ws_resp = await client.post("/api/workspaces", headers=headers, json={"name": "Msg WS"})
    ws_id = ws_resp.json()["id"]
    room_resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms", headers=headers, json={"name": "General"}
    )
    room_id = room_resp.json()["id"]
    return ws_id, room_id


@pytest.mark.asyncio
async def test_send_message(client: AsyncClient, auth_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
        headers=auth_headers,
        json={"content": "Hello world!"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["content"] == "Hello world!"
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_send_message_not_member(client: AsyncClient, auth_headers: dict, second_user_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
        headers=second_user_headers,
        json={"content": "Not allowed"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_send_message_room_not_found(client: AsyncClient, auth_headers: dict):
    ws_resp = await client.post("/api/workspaces", headers=auth_headers, json={"name": "WS"})
    ws_id = ws_resp.json()["id"]
    resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms/nonexistent/messages",
        headers=auth_headers,
        json={"content": "No room"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_messages(client: AsyncClient, auth_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
        headers=auth_headers,
        json={"content": "Message 1"},
    )
    await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
        headers=auth_headers,
        json={"content": "Message 2"},
    )

    resp = await client.get(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    messages = resp.json()
    assert len(messages) == 2
    assert messages[0]["content"] == "Message 1"
    assert messages[1]["content"] == "Message 2"


@pytest.mark.asyncio
async def test_list_messages_with_limit(client: AsyncClient, auth_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    for i in range(5):
        await client.post(
            f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
            headers=auth_headers,
            json={"content": f"Msg {i}"},
        )

    resp = await client.get(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
        headers=auth_headers,
        params={"limit": 2},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_reply_to_message(client: AsyncClient, auth_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    msg_resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
        headers=auth_headers,
        json={"content": "Original message"},
    )
    msg_id = msg_resp.json()["id"]

    reply_resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages/{msg_id}/reply",
        headers=auth_headers,
        json={"content": "This is a reply"},
    )
    assert reply_resp.status_code == 201
    data = reply_resp.json()
    assert data["content"] == "This is a reply"
    assert data["reply_to_id"] == msg_id
    assert data["reply_to_content"] == "Original message"


@pytest.mark.asyncio
async def test_reply_to_nonexistent_message(client: AsyncClient, auth_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages/nonexistent/reply",
        headers=auth_headers,
        json={"content": "No parent"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_send_message_empty_content(client: AsyncClient, auth_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/messages",
        headers=auth_headers,
        json={"content": ""},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_typing_indicator(client: AsyncClient, auth_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    resp = await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/typing",
        headers=auth_headers,
        json={"is_typing": True},
    )
    assert resp.status_code == 204

    resp = await client.get(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/typing",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    typing_users = resp.json()
    assert len(typing_users) == 1
    assert typing_users[0]["username"] == "testuser"


@pytest.mark.asyncio
async def test_typing_indicator_stop(client: AsyncClient, auth_headers: dict):
    ws_id, room_id = await _setup_workspace_and_room(client, auth_headers)
    await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/typing",
        headers=auth_headers,
        json={"is_typing": True},
    )
    await client.post(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/typing",
        headers=auth_headers,
        json={"is_typing": False},
    )

    resp = await client.get(
        f"/api/workspaces/{ws_id}/rooms/{room_id}/typing",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0
