from __future__ import annotations

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import get_database_path, get_database_url
from backend.database import MovieQueries
from backend.routers import admin, auth_router, libraries, movies, stats
from backend.services.task_manager import TaskManager
from database.models import get_db_url

app = FastAPI(
    title="Telegram Movie Library",
    description="REST API exposing the Telegram Movie Library SQLite database.",
    version="1.0.0",
)


# ------------------------------------------------------------------
# Security headers middleware
# ------------------------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        req_host = request.url.hostname or "localhost"
        connect_src = (
            f"connect-src 'self' https://telegram-movie-library.onrender.com "
            f"http://{request.url.netloc} http://localhost:8000 http://127.0.0.1:8000 "
            f"ws://{req_host}:5173 ws://localhost:5173 ws://127.0.0.1:5173;"
        )
        # CSP — restrict resource loading (replaces deprecated X-XSS-Protection)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' https://image.tmdb.org data:; "
            f"{connect_src} "
            "frame-ancestors 'none'"
        )
        # HSTS — only effective over HTTPS, harmless over HTTP
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Prevent caching of authenticated admin API responses
        if request.url.path.startswith("/api/admin"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        return response


app.add_middleware(SecurityHeadersMiddleware)

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
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
 

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
app.include_router(auth_router.router)
app.include_router(admin.router)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Health-check / welcome endpoint."""
    return {
        "service": "Telegram Movie Library API",
        "docs": "/docs",
    }

