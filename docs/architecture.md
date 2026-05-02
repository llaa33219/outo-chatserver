# Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        outo-chatserver                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Frontend   │    │   REST API  │    │  WebSocket  │     │
│  │  (Vanilla JS)│    │   (FastAPI) │    │   (FastAPI) │     │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│         │                   │                   │             │
│         └───────────────────┼───────────────────┘             │
│                             │                               │
│                      ┌──────▼───────┐                       │
│                      │   Services   │                       │
│                      │  (Business)  │                       │
│                      └──────┬───────┘                       │
│                             │                               │
│                      ┌──────▼───────┐                       │
│                      │   Models     │                       │
│                      │ (SQLAlchemy) │                       │
│                      └──────┬───────┘                       │
│                             │                               │
│                      ┌──────▼───────┐                       │
│                      │   Database   │                       │
│                      │   (SQLite)   │                       │
│                      └──────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### Frontend (`app/static/`)

- `index.html` — Single page app shell
- `css/style.css` — Brutalist design styles
- `js/app.js` — SPA router and view rendering
- `js/api.js` — HTTP client wrapper
- `js/chat.js` — Chat and WebSocket logic

### API Layer (`app/api/`)

FastAPI routers handling HTTP requests:

| Module | Endpoints |
|--------|-----------|
| `auth.py` | Register, Login |
| `users.py` | Profile, Settings |
| `friends.py` | Friend CRUD |
| `workspaces.py` | Workspace CRUD |
| `rooms.py` | Room CRUD |
| `messages.py` | Messages, Typing |
| `notifications.py` | Notifications |
| `websocket.py` | WebSocket handler |

### Service Layer (`app/services/`)

Business logic separated from API handlers:

| Module | Responsibility |
|--------|---------------|
| `auth_service.py` | User registration, authentication |
| `user_service.py` | Profile management |
| `friend_service.py` | Friendship operations |
| `workspace_service.py` | Workspace operations |
| `room_service.py` | Room operations |
| `message_service.py` | Message operations |
| `notification_service.py` | Notification operations |
| `typing_manager.py` | In-memory typing state |

### Models (`app/models/`)

SQLAlchemy ORM models:

```
User ─┬─ Workspace (owner)
      ├─ WorkspaceMember
      ├─ Friendship
      ├─ Message
      └─ Notification

Workspace ─┬─ WorkspaceMember
            └─ Room ─ Message
```

### Schemas (`app/schemas/`)

Pydantic models for request/response validation.

---

## Data Flow

### REST Request

```
Client → FastAPI Router → Service → Model → Database
                                    ↓
                              Response JSON
```

### WebSocket

```
Client ←→ WebSocket Handler
              ↓
         TypingManager (in-memory)
              ↓
         Broadcast to Room
```

---

## Security

### Authentication Flow

```
1. POST /api/register → Create User (hashed password)
2. POST /api/token → Verify credentials → Return JWT
3. Request + Bearer Token → Decode JWT → Get User
```

### Password Hashing

- Algorithm: Argon2id
- Memory-hard, GPU-resistant
- OWASP recommended

### Data Encryption

- Algorithm: Fernet (AES-128-CBC)
- Encrypts message content at rest
- Transparent via SQLAlchemy TypeDecorator

---

## Database Schema

### Users

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| username | VARCHAR(50) | Unique username |
| password_hash | VARCHAR(255) | Argon2 hash |
| display_name | VARCHAR(100) | Optional display name |
| settings | JSON | User preferences |
| created_at | TIMESTAMP | Creation time |

### Workspaces

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(100) | Workspace name |
| owner_id | UUID | FK → Users |
| created_at | TIMESTAMP | Creation time |

### Rooms

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| workspace_id | UUID | FK → Workspaces |
| name | VARCHAR(100) | Room name |
| created_by | UUID | FK → Users |
| created_at | TIMESTAMP | Creation time |

### Messages

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| room_id | UUID | FK → Rooms |
| user_id | UUID | FK → Users |
| content | TEXT | Encrypted content |
| reply_to_id | UUID | FK → Messages (nullable) |
| created_at | TIMESTAMP | Creation time |
| deleted_at | TIMESTAMP | Soft delete (nullable) |

---

## Scalability

### Current Limits

- SQLite: Single-file, good for < 100 concurrent users
- In-memory typing state: Lost on restart
- No message pagination in WebSocket

### Scaling Options

1. **PostgreSQL** — Better concurrency
2. **Redis** — Shared typing state, pub/sub
3. **Load Balancer** — Multiple instances
4. **Message Queue** — Async processing
