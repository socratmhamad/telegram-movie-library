from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_database_path, get_database_url
from backend.database import MovieQueries
from backend.routers import admin, libraries, movies, stats
from backend.services.task_manager import TaskManager
from database.models import get_db_url

app = FastAPI(
    title="Telegram Movie Library",
    description="REST API exposing the Telegram Movie Library SQLite database.",
    version="1.0.0",
)

# ------------------------------------------------------------------
# CORS — allow the future Vite dev server and common local origins
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://telegram-movie-library.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
),
 

# ------------------------------------------------------------------
# Shared query layer (stored on app.state for dependency injection)
# ------------------------------------------------------------------
db_url = get_db_url(get_database_url(), get_database_path())
app.state.queries = MovieQueries(db_url)
app.state.tasks = TaskManager()

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------
app.include_router(libraries.router)
app.include_router(movies.router)
app.include_router(stats.router)
app.include_router(admin.router)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Health-check / welcome endpoint."""
    return {
        "service": "Telegram Movie Library API",
        "docs": "/docs",
    }
