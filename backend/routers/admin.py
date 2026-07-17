"""Admin API router — library CRUD, task management, and background operations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func

from backend.auth import get_current_admin
from backend.models import (
    LibraryCreateRequest,
    LibraryUpdateRequest,
    LibraryDetailResponse,
    MigrationRequest,
    TaskListResponse,
    TaskLogsResponse,
    TaskResponse,
)
from backend.services.task_manager import TaskManager
from database.models import init_db, Library, Movie, TMDBMovie, TelegramMessage

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


# ------------------------------------------------------------------
# Dependency helpers
# ------------------------------------------------------------------

def _get_tasks(request: Request) -> TaskManager:
    return request.app.state.tasks  # type: ignore[return-value]


def _get_session_factory(request: Request):
    return request.app.state.queries.SessionLocal


# ------------------------------------------------------------------
# Library CRUD
# ------------------------------------------------------------------

@router.get("/libraries", response_model=list[LibraryDetailResponse])
def admin_list_libraries(request: Request):
    """List ALL libraries with detailed stats (including inactive)."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        libs = session.execute(
            select(Library).order_by(Library.id)
        ).scalars().all()

        result = []
        for lib in libs:
            movie_count = session.scalar(
                select(func.count(Movie.id)).where(Movie.library_id == lib.id)
            ) or 0
            movies_with_tmdb = session.scalar(
                select(func.count(Movie.id)).where(
                    Movie.library_id == lib.id,
                    Movie.tmdb_movie_id.isnot(None),
                )
            ) or 0
            total_messages = session.scalar(
                select(func.count(TelegramMessage.id))
                .join(Movie, TelegramMessage.movie_id == Movie.id)
                .where(Movie.library_id == lib.id)
            ) or 0

            result.append(LibraryDetailResponse(
                id=lib.id,
                name=lib.name,
                slug=lib.slug,
                telegram_channel=lib.telegram_channel,
                telegram_channel_id=lib.telegram_channel_id,
                is_active=lib.is_active,
                movie_count=movie_count,
                movies_with_tmdb=movies_with_tmdb,
                movies_without_tmdb=movie_count - movies_with_tmdb,
                total_messages=total_messages,
            ))
        return result


@router.post("/libraries", response_model=LibraryDetailResponse, status_code=201)
def admin_create_library(body: LibraryCreateRequest, request: Request):
    """Create a new library."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = Library(
            name=body.name,
            slug=body.slug,
            telegram_channel=body.telegram_channel,
            telegram_channel_id=body.telegram_channel_id,
            is_active=body.is_active,
        )
        session.add(lib)
        session.commit()
        session.refresh(lib)
        return LibraryDetailResponse(
            id=lib.id,
            name=lib.name,
            slug=lib.slug,
            telegram_channel=lib.telegram_channel,
            telegram_channel_id=lib.telegram_channel_id,
            is_active=lib.is_active,
        )


@router.put("/libraries/{library_id}", response_model=LibraryDetailResponse)
def admin_update_library(library_id: int, body: LibraryUpdateRequest, request: Request):
    """Update library details."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(Library).where(Library.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "Library not found")

        if body.name is not None:
            lib.name = body.name
        if body.slug is not None:
            lib.slug = body.slug
        if body.telegram_channel is not None:
            lib.telegram_channel = body.telegram_channel
        if body.telegram_channel_id is not None:
            lib.telegram_channel_id = body.telegram_channel_id
        if body.is_active is not None:
            lib.is_active = body.is_active

        session.commit()
        session.refresh(lib)

        movie_count = session.scalar(
            select(func.count(Movie.id)).where(Movie.library_id == lib.id)
        ) or 0
        movies_with_tmdb = session.scalar(
            select(func.count(Movie.id)).where(
                Movie.library_id == lib.id,
                Movie.tmdb_movie_id.isnot(None),
            )
        ) or 0
        total_messages = session.scalar(
            select(func.count(TelegramMessage.id))
            .join(Movie, TelegramMessage.movie_id == Movie.id)
            .where(Movie.library_id == lib.id)
        ) or 0

        return LibraryDetailResponse(
            id=lib.id,
            name=lib.name,
            slug=lib.slug,
            telegram_channel=lib.telegram_channel,
            telegram_channel_id=lib.telegram_channel_id,
            is_active=lib.is_active,
            movie_count=movie_count,
            movies_with_tmdb=movies_with_tmdb,
            movies_without_tmdb=movie_count - movies_with_tmdb,
            total_messages=total_messages,
        )


@router.delete("/libraries/{library_id}", status_code=204)
def admin_delete_library(library_id: int, request: Request):
    """Delete a library and all associated movies/messages."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(Library).where(Library.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "Library not found")

        # Delete telegram messages for all movies in library
        movies = session.execute(
            select(Movie).where(Movie.library_id == library_id)
        ).scalars().all()
        for movie in movies:
            session.query(TelegramMessage).filter(
                TelegramMessage.movie_id == movie.id
            ).delete()
        # Delete movies
        session.query(Movie).filter(Movie.library_id == library_id).delete()
        # Delete library
        session.delete(lib)
        session.commit()
    return None


# ------------------------------------------------------------------
# Task operations
# ------------------------------------------------------------------

@router.post("/libraries/{library_id}/scan", response_model=TaskResponse)
def admin_scan_library(library_id: int, request: Request):
    """Launch scraper for a library's Telegram channel."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(Library).where(Library.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "Library not found")
        channel = lib.telegram_channel

    tasks = _get_tasks(request)
    task = tasks.launch_scan(library_id, channel, f"Scan: {channel}")
    return TaskResponse(**task.to_dict())


@router.post("/libraries/{library_id}/update-tmdb", response_model=TaskResponse)
def admin_update_tmdb(library_id: int, request: Request):
    """Launch TMDB updater for a library."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(Library).where(Library.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "Library not found")

    tasks = _get_tasks(request)
    task = tasks.launch_tmdb_update(library_id, f"TMDB update: library {library_id}")
    return TaskResponse(**task.to_dict())


@router.post("/libraries/{library_id}/migrate", response_model=TaskResponse)
def admin_migrate_library(library_id: int, body: MigrationRequest, request: Request):
    """Launch channel migration for a library."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(Library).where(Library.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "Library not found")

    tasks = _get_tasks(request)
    task = tasks.launch_migration(
        library_id,
        body.new_channel,
        body.new_channel_id,
        body.dry_run,
        f"Migration: library {library_id}" + (" (dry-run)" if body.dry_run else ""),
    )
    return TaskResponse(**task.to_dict())


# ------------------------------------------------------------------
# Task status & logs
# ------------------------------------------------------------------

@router.get("/tasks", response_model=TaskListResponse)
def admin_list_tasks(request: Request):
    """List all background tasks."""
    tasks = _get_tasks(request)
    return TaskListResponse(
        tasks=[TaskResponse(**t.to_dict()) for t in tasks.get_all_tasks()]
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def admin_get_task(task_id: str, request: Request):
    """Get status of a specific task."""
    tasks = _get_tasks(request)
    task = tasks.get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return TaskResponse(**task.to_dict())


@router.get("/tasks/{task_id}/logs", response_model=TaskLogsResponse)
def admin_get_task_logs(task_id: str, request: Request):
    """Get log output for a task."""
    tasks = _get_tasks(request)
    task = tasks.get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    logs = tasks.get_task_logs(task_id)
    return TaskLogsResponse(task_id=task_id, logs=logs)


@router.post("/tasks/{task_id}/cancel", response_model=TaskResponse)
def admin_cancel_task(task_id: str, request: Request):
    """Cancel a running task."""
    tasks = _get_tasks(request)
    task = tasks.get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    tasks.cancel_task(task_id)
    return TaskResponse(**task.to_dict())
