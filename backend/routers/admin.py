"""Admin API router — library CRUD, task management, and background operations."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from sqlalchemy import select, func

from backend.auth import get_current_admin
from backend.models import (
    LibraryCreateRequest,
    LibraryUpdateRequest,
    LibraryDetailResponse,
    LibraryReorderRequest,
    MigrationRequest,
    TaskListResponse,
    TaskLogsResponse,
    TaskResponse,
)
from backend.services.task_manager import TaskManager
from backend.tv_models import (
    TVLibraryCreateRequest,
    TVLibraryUpdateRequest,
    TVLibraryDetailResponse,
    TVLibraryReorderRequest,
    FeaturedTVCreateRequest,
    FeaturedTVUpdateRequest,
    FeaturedTVResponse,
    FeaturedTVListResponse,
)
from database.models import init_db, Library, Movie, TMDBMovie, TelegramMessage
from database.tv_models import TVLibrary, TVSeries, TMDBTVSeries

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
            select(Library).order_by(Library.display_order.asc(), Library.id.asc())
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
                name_en=lib.name_en,
                slug=lib.slug,
                telegram_channel=lib.telegram_channel,
                telegram_channel_id=lib.telegram_channel_id,
                is_active=lib.is_active,
                movie_count=movie_count,
                movies_with_tmdb=movies_with_tmdb,
                movies_without_tmdb=movie_count - movies_with_tmdb,
                total_messages=total_messages,
                display_order=lib.display_order if lib.display_order is not None else 0,
            ))
        return result


@router.post("/libraries", response_model=LibraryDetailResponse, status_code=201)
def admin_create_library(body: LibraryCreateRequest, request: Request):
    """Create a new library."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        if body.display_order is not None:
            display_order = body.display_order
        else:
            max_order = session.scalar(select(func.max(Library.display_order))) or 0
            display_order = max_order + 1

        lib = Library(
            name=body.name,
            name_en=body.name_en,
            slug=body.slug,
            telegram_channel=body.telegram_channel,
            telegram_channel_id=body.telegram_channel_id,
            is_active=body.is_active,
            display_order=display_order,
        )
        session.add(lib)
        session.commit()
        session.refresh(lib)
        return LibraryDetailResponse(
            id=lib.id,
            name=lib.name,
            name_en=lib.name_en,
            slug=lib.slug,
            telegram_channel=lib.telegram_channel,
            telegram_channel_id=lib.telegram_channel_id,
            is_active=lib.is_active,
            display_order=lib.display_order if lib.display_order is not None else 0,
        )


@router.put("/libraries/reorder")
def admin_reorder_libraries(body: LibraryReorderRequest, request: Request):
    """Batch reorder movie libraries."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        if body.ids is not None:
            for idx, lib_id in enumerate(body.ids, start=1):
                session.query(Library).filter(Library.id == lib_id).update({"display_order": idx})
        elif body.items is not None:
            for item in body.items:
                lib_id = item.id if hasattr(item, "id") else item.get("id")
                order = item.display_order if hasattr(item, "display_order") else item.get("display_order", 0)
                if lib_id is not None:
                    session.query(Library).filter(Library.id == lib_id).update({"display_order": order})
        session.commit()
    return {"status": "ok"}


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
        if body.name_en is not None:
            lib.name_en = body.name_en
        if body.slug is not None:
            lib.slug = body.slug
        if body.telegram_channel is not None:
            lib.telegram_channel = body.telegram_channel
        if body.telegram_channel_id is not None:
            lib.telegram_channel_id = body.telegram_channel_id
        if body.is_active is not None:
            lib.is_active = body.is_active
        if body.display_order is not None:
            lib.display_order = body.display_order

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
            name_en=lib.name_en,
            slug=lib.slug,
            telegram_channel=lib.telegram_channel,
            telegram_channel_id=lib.telegram_channel_id,
            is_active=lib.is_active,
            movie_count=movie_count,
            movies_with_tmdb=movies_with_tmdb,
            movies_without_tmdb=movie_count - movies_with_tmdb,
            total_messages=total_messages,
            display_order=lib.display_order if lib.display_order is not None else 0,
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


@router.post("/tv-libraries/{library_id}/migrate", response_model=TaskResponse)
def admin_migrate_tv_library(library_id: int, body: MigrationRequest, request: Request):
    """Launch channel migration for a TV library."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(TVLibrary).where(TVLibrary.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "TV Library not found")

    tasks = _get_tasks(request)
    task = tasks.launch_tv_migration(
        library_id,
        body.new_channel,
        body.new_channel_id,
        body.dry_run,
        f"TV Migration: library {library_id}" + (" (dry-run)" if body.dry_run else ""),
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


# ------------------------------------------------------------------
# TV Series admin endpoints
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# TV Library CRUD & Tasks
# ------------------------------------------------------------------

@router.get("/tv-libraries", response_model=list[TVLibraryDetailResponse])
def admin_list_tv_libraries(request: Request):
    """List ALL TV libraries with detailed stats."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        libs = session.execute(
            select(TVLibrary).order_by(TVLibrary.display_order.asc(), TVLibrary.id.asc())
        ).scalars().all()

        result = []
        for lib in libs:
            series_count = session.scalar(
                select(func.count(TVSeries.id)).where(TVSeries.library_id == lib.id)
            ) or 0
            series_with_tmdb = session.scalar(
                select(func.count(TVSeries.id)).where(
                    TVSeries.library_id == lib.id,
                    TVSeries.tmdb_tv_id.isnot(None),
                )
            ) or 0

            result.append(TVLibraryDetailResponse(
                id=lib.id,
                name=lib.name,
                name_en=lib.name_en,
                slug=lib.slug,
                telegram_channel=lib.telegram_channel,
                telegram_channel_id=lib.telegram_channel_id,
                is_active=lib.is_active,
                series_count=series_count,
                series_with_tmdb=series_with_tmdb,
                series_without_tmdb=series_count - series_with_tmdb,
                display_order=lib.display_order if lib.display_order is not None else 0,
            ))
        return result


@router.post("/tv-libraries", response_model=TVLibraryDetailResponse, status_code=201)
def admin_create_tv_library(body: TVLibraryCreateRequest, request: Request):
    """Create a new TV series library."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        if body.display_order is not None:
            display_order = body.display_order
        else:
            max_order = session.scalar(select(func.max(TVLibrary.display_order))) or 0
            display_order = max_order + 1

        lib = TVLibrary(
            name=body.name,
            name_en=body.name_en,
            slug=body.slug,
            telegram_channel=body.telegram_channel,
            telegram_channel_id=body.telegram_channel_id,
            is_active=body.is_active,
            display_order=display_order,
        )
        session.add(lib)
        session.commit()
        session.refresh(lib)
        return TVLibraryDetailResponse(
            id=lib.id,
            name=lib.name,
            name_en=lib.name_en,
            slug=lib.slug,
            telegram_channel=lib.telegram_channel,
            telegram_channel_id=lib.telegram_channel_id,
            is_active=lib.is_active,
            display_order=lib.display_order if lib.display_order is not None else 0,
        )


@router.put("/tv-libraries/reorder")
def admin_reorder_tv_libraries(body: TVLibraryReorderRequest, request: Request):
    """Batch reorder TV libraries."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        if body.ids is not None:
            for idx, lib_id in enumerate(body.ids, start=1):
                session.query(TVLibrary).filter(TVLibrary.id == lib_id).update({"display_order": idx})
        elif body.items is not None:
            for item in body.items:
                lib_id = item.id if hasattr(item, "id") else item.get("id")
                order = item.display_order if hasattr(item, "display_order") else item.get("display_order", 0)
                if lib_id is not None:
                    session.query(TVLibrary).filter(TVLibrary.id == lib_id).update({"display_order": order})
        session.commit()
    return {"status": "ok"}


@router.put("/tv-libraries/{library_id}", response_model=TVLibraryDetailResponse)
def admin_update_tv_library(library_id: int, body: TVLibraryUpdateRequest, request: Request):
    """Update TV series library details."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(TVLibrary).where(TVLibrary.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "TV Library not found")

        if body.name is not None:
            lib.name = body.name
        if body.name_en is not None:
            lib.name_en = body.name_en
        if body.slug is not None:
            lib.slug = body.slug
        if body.telegram_channel is not None:
            lib.telegram_channel = body.telegram_channel
        if body.telegram_channel_id is not None:
            lib.telegram_channel_id = body.telegram_channel_id
        if body.is_active is not None:
            lib.is_active = body.is_active
        if body.display_order is not None:
            lib.display_order = body.display_order

        session.commit()
        session.refresh(lib)

        series_count = session.scalar(
            select(func.count(TVSeries.id)).where(TVSeries.library_id == lib.id)
        ) or 0
        series_with_tmdb = session.scalar(
            select(func.count(TVSeries.id)).where(
                TVSeries.library_id == lib.id,
                TVSeries.tmdb_tv_id.isnot(None),
            )
        ) or 0

        return TVLibraryDetailResponse(
            id=lib.id,
            name=lib.name,
            name_en=lib.name_en,
            slug=lib.slug,
            telegram_channel=lib.telegram_channel,
            telegram_channel_id=lib.telegram_channel_id,
            is_active=lib.is_active,
            series_count=series_count,
            series_with_tmdb=series_with_tmdb,
            series_without_tmdb=series_count - series_with_tmdb,
            display_order=lib.display_order if lib.display_order is not None else 0,
        )


@router.delete("/tv-libraries/{library_id}", status_code=204)
def admin_delete_tv_library(library_id: int, request: Request):
    """Delete a TV library and all its associated series."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(TVLibrary).where(TVLibrary.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "TV Library not found")

        session.query(TVSeries).filter(TVSeries.library_id == library_id).delete()
        session.delete(lib)
        session.commit()
    return None


@router.post("/tv-libraries/{library_id}/scan", response_model=TaskResponse)
def admin_scan_tv_library(library_id: int, request: Request):
    """Launch scraper for a TV library's Telegram channel."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(TVLibrary).where(TVLibrary.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "TV Library not found")
        channel = lib.telegram_channel

    tasks = _get_tasks(request)
    task = tasks.launch_tv_scan(library_id, channel, f"TV Scan: {channel}")
    return TaskResponse(**task.to_dict())


@router.post("/tv-libraries/{library_id}/update-tmdb", response_model=TaskResponse)
def admin_update_tv_tmdb_library(library_id: int, request: Request):
    """Launch TMDB updater for a TV library."""
    SessionLocal = _get_session_factory(request)
    with SessionLocal() as session:
        lib = session.execute(
            select(TVLibrary).where(TVLibrary.id == library_id)
        ).scalar_one_or_none()
        if not lib:
            raise HTTPException(404, "TV Library not found")

    tasks = _get_tasks(request)
    task = tasks.launch_tv_tmdb_update(library_id, f"TV TMDB update: library {library_id}")
    return TaskResponse(**task.to_dict())


# ------------------------------------------------------------------
# File Upload Endpoint
# ------------------------------------------------------------------

@router.post("/upload-image")
async def admin_upload_image(file: UploadFile = File(...)):
    """Upload a custom image/poster file and return the access URL."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image (jpg, png, webp, etc.)")

    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "image.jpg").suffix.lower()
    if not ext or ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]:
        ext = ".jpg"

    filename = f"{uuid.uuid4().hex}{ext}"
    target_path = upload_dir / filename

    content = await file.read()
    with open(target_path, "wb") as f:
        f.write(content)

    return {"url": f"/uploads/{filename}"}


# ------------------------------------------------------------------
# Featured TV Series CRUD Endpoints
# ------------------------------------------------------------------

@router.get("/featured-tv", response_model=FeaturedTVListResponse)
def admin_list_featured_tv(request: Request) -> FeaturedTVListResponse:
    """Return all manually managed featured TV series entries."""
    series_queries = request.app.state.series_queries
    return FeaturedTVListResponse(items=series_queries.get_featured_tv_series())


@router.post("/featured-tv", response_model=FeaturedTVResponse)
def admin_create_featured_tv(body: FeaturedTVCreateRequest, request: Request) -> FeaturedTVResponse:
    """Create a new manually managed featured TV series entry."""
    series_queries = request.app.state.series_queries
    created = series_queries.create_featured_tv_series(body.model_dump())
    return FeaturedTVResponse(**created)


@router.put("/featured-tv/{item_id}", response_model=FeaturedTVResponse)
def admin_update_featured_tv(item_id: int, body: FeaturedTVUpdateRequest, request: Request) -> FeaturedTVResponse:
    """Update an existing featured TV series entry."""
    series_queries = request.app.state.series_queries
    updated = series_queries.update_featured_tv_series(item_id, body.model_dump(exclude_unset=True))
    if updated is None:
        raise HTTPException(404, "Featured TV Series entry not found")
    return FeaturedTVResponse(**updated)


@router.delete("/featured-tv/{item_id}")
def admin_delete_featured_tv(item_id: int, request: Request):
    """Delete a featured TV series entry."""
    series_queries = request.app.state.series_queries
    success = series_queries.delete_featured_tv_series(item_id)
    if not success:
        raise HTTPException(404, "Featured TV Series entry not found")
    return {"status": "success", "message": f"Deleted featured TV series {item_id}"}

