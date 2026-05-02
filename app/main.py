from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.database import init_db
from app.api import auth, users, friends, workspaces, rooms, messages, notifications, help, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="outo-chatserver",
    description="Self-hosted chat server with REST API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(workspaces.router)
app.include_router(rooms.router)
app.include_router(messages.router)
app.include_router(notifications.router)
app.include_router(help.router)
app.include_router(websocket.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/css/{file_path:path}")
async def css(file_path: str):
    return FileResponse(os.path.join(static_dir, "css", file_path))


@app.get("/js/{file_path:path}")
async def js(file_path: str):
    return FileResponse(os.path.join(static_dir, "js", file_path))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
