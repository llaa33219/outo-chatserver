# Configuration Guide

## Environment Variables

All configuration is done via `.env` file in the project root.

### Database

```env
DATABASE_URL=sqlite+aiosqlite:///./data/chat.db
```

| Value | Description |
|-------|-------------|
| `sqlite+aiosqlite:///./data/chat.db` | SQLite (default, zero-config) |
| `postgresql+asyncpg://user:pass@host/db` | PostgreSQL (production) |

---

### Security

```env
SECRET_KEY=your-secret-key-min-32-characters
TOKEN_EXPIRE_HOURS=24
ENCRYPTION_KEY=your-fernet-key
```

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (min 32 chars) | Required |
| `TOKEN_EXPIRE_HOURS` | Token validity period | `24` |
| `ENCRYPTION_KEY` | Fernet key for data encryption | Required |

#### Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Generate ENCRYPTION_KEY

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

### Server

```env
HOST=0.0.0.0
PORT=18279
```

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Bind address | `0.0.0.0` |
| `PORT` | Listen port | `18279` |

---

## Complete .env Example

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/chat.db

# Security
SECRET_KEY=change-me-to-a-random-secret-key-min-32-chars
TOKEN_EXPIRE_HOURS=24
ENCRYPTION_KEY=change-me-fernet-key

# Server
HOST=0.0.0.0
PORT=18279
```

---

## Token Expiry

Tokens expire after `TOKEN_EXPIRE_HOURS` hours. Users must re-authenticate after expiry.

Recommended values:
- Development: `24` (1 day)
- Production: `8` (1 work day) or `72` (3 days)

---

## Encryption

Message content is encrypted at rest using Fernet symmetric encryption.

**Important:** 
- Back up your `ENCRYPTION_KEY`
- Losing the key means losing access to encrypted data
- Changing the key requires re-encrypting all data

---

## Database Migration

### SQLite to PostgreSQL

1. Export data from SQLite
2. Update `DATABASE_URL` in `.env`
3. Install `asyncpg`: `pip install asyncpg`
4. Import data to PostgreSQL
5. Restart server

### Backup SQLite

```bash
cp data/chat.db data/chat.db.backup
```
