from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_database_path
from backend.database import MovieQueries
from backend.routers import movies, stats

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
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Shared query layer (stored on app.state for dependency injection)
# ------------------------------------------------------------------
app.state.queries = MovieQueries(get_database_path())

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------
app.include_router(movies.router)
app.include_router(stats.router)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Health-check / welcome endpoint."""
    return {
        "service": "Telegram Movie Library API",
        "docs": "/docs",
    }
