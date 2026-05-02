# API Reference

## Authentication

All authenticated endpoints require `Authorization: Bearer <token>` header.

### Register

```
POST /api/register
```

**Auth:** No

**Request Body:**
```json
{
  "username": "string (3-50 chars)",
  "password": "string (8-100 chars)"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "string",
  "display_name": null,
  "created_at": "2026-04-29T12:00:00Z"
}
```

**Errors:**
- `400` — Username already exists

---

### Login

```
POST /api/token
```

**Auth:** No

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors:**
- `401` — Invalid credentials

---

## Users

### Get Profile

```
GET /api/me
```

**Auth:** Yes

**Response (200):**
```json
{
  "id": "uuid",
  "username": "string",
  "display_name": "string|null",
  "created_at": "2026-04-29T12:00:00Z"
}
```

---

### Update Settings

```
PUT /api/me/settings
```

**Auth:** Yes

**Request Body:**
```json
{
  "display_name": "string (max 100)",
  "settings": {}
}
```

**Response (200):** Updated user object

---

## Friends

### List Friends

```
GET /api/friends
```

**Auth:** Yes

**Response (200):**
```json
[
  {
    "id": "uuid",
    "username": "string",
    "display_name": "string|null",
    "status": "accepted",
    "since": "2026-04-29T12:00:00Z"
  }
]
```

---

### Add Friend

```
POST /api/friends
```

**Auth:** Yes

**Request Body:**
```json
{
  "friend_id": "uuid"
}
```

**Response (201):** Friend object

**Errors:**
- `400` — Cannot add yourself
- `404` — User not found
- `409` — Friendship already exists

---

### Remove Friend

```
DELETE /api/friends/{friend_id}
```

**Auth:** Yes

**Response (204):** No content

**Errors:**
- `404` — Friendship not found

---

## Workspaces

### List Workspaces

```
GET /api/workspaces
```

**Auth:** Yes

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "string",
    "owner_id": "uuid",
    "member_count": 5,
    "created_at": "2026-04-29T12:00:00Z"
  }
]
```

---

### Create Workspace

```
POST /api/workspaces
```

**Auth:** Yes

**Request Body:**
```json
{
  "name": "string (1-100 chars)"
}
```

**Response (201):** Workspace object

---

### Join Workspace

```
POST /api/workspaces/{workspace_id}/join
```

**Auth:** Yes

**Response (200):** Workspace object

**Errors:**
- `404` — Workspace not found

---

### Delete Workspace

```
DELETE /api/workspaces/{workspace_id}
```

**Auth:** Yes (owner only)

**Response (204):** No content

**Errors:**
- `404` — Workspace not found or not owner

---

## Rooms

### List Rooms

```
GET /api/workspaces/{workspace_id}/rooms
```

**Auth:** Yes (member only)

**Response (200):**
```json
[
  {
    "id": "uuid",
    "workspace_id": "uuid",
    "name": "string",
    "created_by": "uuid",
    "created_at": "2026-04-29T12:00:00Z"
  }
]
```

**Errors:**
- `403` — Not a member

---

### Create Room

```
POST /api/workspaces/{workspace_id}/rooms
```

**Auth:** Yes (member only)

**Request Body:**
```json
{
  "name": "string (1-100 chars)"
}
```

**Response (201):** Room object

**Errors:**
- `403` — Not a member

---

### Delete Room

```
DELETE /api/workspaces/{workspace_id}/rooms/{room_id}
```

**Auth:** Yes (workspace owner only)

**Response (204):** No content

**Errors:**
- `403` — Not owner
- `404` — Room not found

---

## Messages

### List Messages

```
GET /api/workspaces/{workspace_id}/rooms/{room_id}/messages
```

**Auth:** Yes (member only)

**Query Parameters:**
- `limit` — Number of messages (1-100, default 50)
- `before` — Message ID for pagination

**Response (200):**
```json
[
  {
    "id": "uuid",
    "room_id": "uuid",
    "user_id": "uuid",
    "username": "string",
    "content": "string",
    "reply_to_id": "uuid|null",
    "reply_to_content": "string|null",
    "created_at": "2026-04-29T12:00:00Z"
  }
]
```

**Errors:**
- `403` — Not a member
- `404` — Room not found

---

### Send Message

```
POST /api/workspaces/{workspace_id}/rooms/{room_id}/messages
```

**Auth:** Yes (member only)

**Request Body:**
```json
{
  "content": "string (1-10000 chars)"
}
```

**Response (201):** Message object

**Errors:**
- `403` — Not a member
- `404` — Room not found

---

### Reply to Message

```
POST /api/workspaces/{workspace_id}/rooms/{room_id}/messages/{message_id}/reply
```

**Auth:** Yes (member only)

**Request Body:**
```json
{
  "content": "string (1-10000 chars)"
}
```

**Response (201):** Message object with `reply_to_id` and `reply_to_content`

**Errors:**
- `403` — Not a member
- `404` — Room or parent message not found

---

## Typing Indicators

### Set Typing Status

```
POST /api/workspaces/{workspace_id}/rooms/{room_id}/typing
```

**Auth:** Yes (member only)

**Request Body:**
```json
{
  "is_typing": true
}
```

**Response (204):** No content

---

### Get Typing Users

```
GET /api/workspaces/{workspace_id}/rooms/{room_id}/typing
```

**Auth:** Yes (member only)

**Response (200):**
```json
[
  {
    "user_id": "uuid",
    "username": "string"
  }
]
```

---

## Notifications

### List Notifications

```
GET /api/notifications
```

**Auth:** Yes

**Query Parameters:**
- `unread` — Filter unread only (boolean, default false)

**Response (200):**
```json
[
  {
    "id": 1,
    "type": "friend_request",
    "payload": {},
    "read": false,
    "created_at": "2026-04-29T12:00:00Z"
  }
]
```

---

### Mark as Read

```
PUT /api/notifications/{notification_id}/read
```

**Auth:** Yes

**Response (200):** Updated notification object

**Errors:**
- `404` — Notification not found

---

## Help

### Get API Reference

```
GET /api/help
```

**Auth:** No

**Response (200):** JSON with all endpoint documentation
