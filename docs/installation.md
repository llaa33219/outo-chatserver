# Installation Guide

## Prerequisites

- Python 3.11+
- pip (Python package manager)

## Quick Install

```bash
# Clone repository
git clone https://github.com/yourusername/outo-chatserver.git
cd outo-chatserver

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"

# Run server
python run.py
```

Server starts at `http://localhost:18279`

---

## Manual Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy aiosqlite python-jose argon2-cffi pydantic pydantic-settings cryptography
```

### 3. Configure Environment

Copy `.env.example` to `.env` and edit:

```bash
cp .env.example .env
```

Required settings:
- `SECRET_KEY` — Random string (min 32 chars)
- `ENCRYPTION_KEY` — Fernet key for data encryption

Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Initialize Database

Database is auto-created on first run.

### 5. Run Server

```bash
python run.py
```

---

## Docker Installation

### Build Image

```bash
docker build -t outo-chatserver .
```

### Run Container

```bash
docker run -d \
  -p 18279:18279 \
  -v ./data:/app/data \
  -v ./.env:/app/.env \
  --name outo-chat \
  outo-chatserver
```

---

## Production Deployment

### 1. Use PostgreSQL (Optional)

Update `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
```

Install asyncpg:
```bash
pip install asyncpg
```

### 2. Use Reverse Proxy

nginx example:
```nginx
server {
    listen 80;
    server_name chat.example.com;

    location / {
        proxy_pass http://127.0.0.1:18279;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 3. Enable HTTPS

Use certbot or similar for SSL certificates.

### 4. Run as Service

Create systemd service `/etc/systemd/system/outo-chat.service`:
```ini
[Unit]
Description=Outo Chat Server
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/outo-chatserver
Environment="PATH=/opt/outo-chatserver/venv/bin"
ExecStart=/opt/outo-chatserver/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable outo-chat
sudo systemctl start outo-chat
```

---

## Troubleshooting

### Port already in use

```bash
# Find process using port
lsof -i :18279

# Kill process
kill -9 <PID>
```

### Database locked

Ensure only one instance is running.

### Permission denied

```bash
chmod +x run.py
```
