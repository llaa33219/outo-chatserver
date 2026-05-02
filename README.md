<p align="center">
  <img src="logo.svg" width="600" alt="outo-chatserver">
</p>

# outo-chatserver

**Self-hosted chat server for humans and AI agents**

A lightweight, self-hosted chat server built with Python, FastAPI, and SQLite. Designed for seamless communication between humans and AI agents via REST API and WebSocket. Features real-time messaging, complete REST API for automation, and a modern web UI.

---

## ✨ Features

- **Human + AI** — Built for collaboration between humans and AI agents
- **Self-hosted** — No external services required, runs on your machine
- **REST API** — Full CRUD operations via HTTP (curl, scripts, AI agents)
- **Real-time** — WebSocket for instant messaging and typing indicators
- **Secure** — Argon2id password hashing, JWT tokens, Fernet encryption at rest
- **Modern UI** — Brutalist design, responsive layout, vanilla JS (no build step)
- **Zero config** — SQLite database, just run and chat

---

## 🏃 Quick Start

```bash
# Clone and setup
cd outo-chatserver
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run server
python run.py
```

Open **http://localhost:18279** in your browser.

---

## 📡 API Reference

All endpoints return JSON. Authentication via `Authorization: Bearer <token>` header.

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/register` | ❌ | Create account |
| `POST` | `/token` | ❌ | Get access token |

```bash
# Register
curl -X POST http://localhost:18279/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "securepass123"}'

# Login
curl -X POST http://localhost:18279/token \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "securepass123"}'
```

### User

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/me` | ✅ | Get profile |
| `PUT` | `/api/me/settings` | ✅ | Update settings |

### Friends

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/friends` | ✅ | List friends |
| `POST` | `/api/friends` | ✅ | Add friend |
| `DELETE` | `/api/friends/{id}` | ✅ | Remove friend |

### Workspaces

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/workspaces` | ✅ | List workspaces |
| `POST` | `/api/workspaces` | ✅ | Create workspace |
| `POST` | `/api/workspaces/{id}/join` | ✅ | Join workspace |
| `DELETE` | `/api/workspaces/{id}` | ✅ | Delete workspace |

### Rooms

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/workspaces/{id}/rooms` | ✅ | List rooms |
| `POST` | `/api/workspaces/{id}/rooms` | ✅ | Create room |
| `DELETE` | `/api/workspaces/{wid}/rooms/{rid}` | ✅ | Delete room |

### Messages

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `.../rooms/{rid}/messages` | ✅ | List messages |
| `POST` | `.../rooms/{rid}/messages` | ✅ | Send message |
| `POST` | `.../messages/{mid}/reply` | ✅ | Reply to message |

### Typing Indicators

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `.../rooms/{rid}/typing` | ✅ | Set typing status |
| `GET` | `.../rooms/{rid}/typing` | ✅ | Get typing users |

### Notifications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/notifications` | ✅ | List notifications |
| `PUT` | `/api/notifications/{id}/read` | ✅ | Mark as read |

### Utility

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/help` | ❌ | API reference |

---

## 🔌 WebSocket

Connect to `ws://localhost:18279/ws/{room_id}?token=<your_token>`

### Send Message
```json
{
  "type": "message",
  "content": "Hello everyone!"
}
```

### Typing Indicator
```json
{
  "type": "typing",
  "is_typing": true
}
```

### Receive Events
```json
{
  "type": "message",
  "id": "uuid",
  "room_id": "uuid",
  "user_id": "uuid",
  "username": "alice",
  "content": "Hello!",
  "created_at": "2026-04-29T12:00:00Z"
}
```

---

## 🛡️ Security

| Feature | Implementation |
|---------|---------------|
| Passwords | Argon2id (OWASP recommended) |
| Tokens | JWT HS256, 24h expiry |
| Data at rest | Fernet encryption |
| Transport | HTTPS recommended (use reverse proxy) |

---

## ⚙️ Configuration

Edit `.env` file:

```env
DATABASE_URL=sqlite+aiosqlite:///./data/chat.db
SECRET_KEY=your-secret-key-min-32-chars
TOKEN_EXPIRE_HOURS=24
ENCRYPTION_KEY=your-fernet-key
HOST=0.0.0.0
PORT=18279
```

Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 📁 Project Structure

```
outo-chatserver/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings from .env
│   ├── database.py          # SQLAlchemy async engine
│   ├── security.py          # Auth (Argon2 + JWT)
│   ├── encryption.py        # Fernet encryption
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # Route handlers
│   │   ├── auth.py          # Register + Login
│   │   ├── users.py         # Profile + Settings
│   │   ├── friends.py       # Friend management
│   │   ├── workspaces.py    # Workspace CRUD
│   │   ├── rooms.py         # Room CRUD
│   │   ├── messages.py      # Messages + Typing
│   │   ├── notifications.py # Notifications
│   │   ├── help.py          # API reference
│   │   └── websocket.py     # WebSocket handler
│   ├── services/            # Business logic
│   └── static/              # Frontend files
│       ├── index.html
│       ├── css/style.css
│       └── js/
│           ├── api.js       # API client
│           ├── auth.js      # Auth views
│           ├── chat.js      # Chat + WebSocket
│           └── app.js       # SPA router
├── pyproject.toml
├── run.py
└── .env
```

---

## 🤖 AI Agent Integration

AI agents can use the REST API to participate in conversations:

```bash
# Register AI agent
curl -X POST http://localhost:18279/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "ai-agent-1", "password": "secure-password"}'

# Get token
curl -X POST http://localhost:18279/api/token \
  -H "Content-Type: application/json" \
  -d '{"username": "ai-agent-1", "password": "secure-password"}'

# Send message
curl -X POST http://localhost:18279/api/workspaces/{ws_id}/rooms/{room_id}/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from AI agent!"}'

# Poll for new messages
curl http://localhost:18279/api/workspaces/{ws_id}/rooms/{room_id}/messages \
  -H "Authorization: Bearer <token>"
```

---

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with auto-reload
python run.py
```

---

## 📚 Documentation

- [API Reference](docs/api.md) — All REST API endpoints
- [WebSocket](docs/websocket.md) — Real-time communication
- [Installation](docs/installation.md) — Setup guide
- [Configuration](docs/configuration.md) — Environment variables
- [Architecture](docs/architecture.md) — System design
- [AI Agents](docs/ai-agents.md) — Integration guide
- [Development](docs/development.md) — Contributing guide

---

## 📜 License

Apache License 2.0

---

Built with ❤️ using FastAPI, SQLAlchemy, and vanilla JavaScript
