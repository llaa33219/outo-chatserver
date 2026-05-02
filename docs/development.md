# Development Guide

## Setup

```bash
# Clone and install
git clone https://github.com/yourusername/outo-chatserver.git
cd outo-chatserver
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

---

## Project Structure

```
outo-chatserver/
├── app/
│   ├── main.py              # FastAPI app, middleware, routes
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # SQLAlchemy engine/session
│   ├── security.py          # Auth (Argon2 + JWT)
│   ├── encryption.py        # Fernet encryption
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # Route handlers
│   ├── services/            # Business logic
│   └── static/              # Frontend files
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml           # Project config
├── run.py                   # Entry point
└── .env                     # Environment variables
```

---

## Running

### Development

```bash
python run.py
```

Auto-reloads on file changes.

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 18279 --workers 4
```

---

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test

```bash
pytest tests/test_auth.py -v
```

---

## Adding New Features

### 1. Create Model

`app/models/example.py`:
```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Example(Base):
    __tablename__ = "examples"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
```

### 2. Create Schema

`app/schemas/example.py`:
```python
from pydantic import BaseModel

class ExampleCreate(BaseModel):
    name: str

class ExampleOut(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
```

### 3. Create Service

`app/services/example_service.py`:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Example

async def create_example(db: AsyncSession, name: str) -> Example:
    example = Example(name=name)
    db.add(example)
    await db.flush()
    return example
```

### 4. Create Router

`app/api/examples.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.example import ExampleCreate, ExampleOut
from app.services import example_service

router = APIRouter(prefix="/api", tags=["examples"])

@router.post("/examples", response_model=ExampleOut)
async def create(data: ExampleCreate, db: AsyncSession = Depends(get_db)):
    return await example_service.create_example(db, data.name)
```

### 5. Register Router

`app/main.py`:
```python
from app.api import examples

app.include_router(examples.router)
```

---

## Code Style

- Python 3.11+ features (type hints, async/await)
- No comments unless necessary
- Self-documenting code
- Type everything

---

## Database Migrations

### Using Alembic

```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

---

## Debugging

### Enable SQL Logging

`app/config.py`:
```python
engine = create_async_engine(url, echo=True)
```

### VS Code Launch Config

`.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload"],
            "jinja": true
        }
    ]
}
```

---

## Common Issues

### Import Errors

Ensure package is installed in editable mode:
```bash
pip install -e .
```

### Database Locked

Only one process can write to SQLite at a time. Use PostgreSQL for concurrent access.

### CORS Errors

CORS is enabled for all origins in development. Configure properly for production.
