from __future__ import annotations

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from pydantic import BaseModel

from config import settings
from backend.services.telegram_links import telegram_link_service
from backend.services.library_import import library_import_service
import backend.database

router = APIRouter(prefix="/api/libraries/{library_slug}/telegram", tags=["telegram"])

def _get_queries(request: Request) -> backend.database.MovieQueries:
    return request.app.state.queries  # type: ignore[return-value]

def _get_library(
    library_slug: str,
    queries: backend.database.MovieQueries = Depends(_get_queries)
) -> dict:
    lib = queries.get_library_by_slug(library_slug)
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    return lib

@router.get("/config")
async def get_config(lib: dict = Depends(_get_library)):
    """Returns the current telegram channel for this library."""
    return {"current_channel": lib["telegram_channel"]}

@router.post("/test-connection")
async def test_connection(
    lib: dict = Depends(_get_library),
    queries: backend.database.MovieQueries = Depends(_get_queries)
):
    """Tests connection to the specified Telegram channel and saves its numeric ID."""
    # Both services inherit from BaseTelegramTask which has test_connection
    success, channel_id = await telegram_link_service.test_connection(lib["telegram_channel"])
    
    if not success:
        raise HTTPException(status_code=400, detail="Could not connect to the specified channel. Check if it exists and credentials are correct.")
        
    if channel_id and channel_id != lib.get("telegram_channel_id"):
        queries.update_library(
            old_slug=lib["slug"],
            name=lib["name"],
            slug=lib["slug"],
            telegram_channel=lib["telegram_channel"],
            telegram_channel_id=channel_id,
            is_active=lib["is_active"]
        )
        
    return {"status": "success", "message": f"Successfully connected to channel (ID: {channel_id})."}

@router.post("/import")
async def import_library(
    background_tasks: BackgroundTasks,
    lib: dict = Depends(_get_library)
):
    """Starts a full import scrape of the library's channel."""
    if telegram_link_service.is_running() or library_import_service.is_running():
        raise HTTPException(status_code=400, detail="A task is already running.")
        
    try:
        library_import_service.start_import(
            library_id=lib["id"], 
            target_channel=lib["telegram_channel"], 
            background_tasks=background_tasks
        )
        return {"status": "started", "mode": "import"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-links")
async def update_links(
    background_tasks: BackgroundTasks,
    lib: dict = Depends(_get_library)
):
    """Starts an execution run to update telegram links."""
    if telegram_link_service.is_running() or library_import_service.is_running():
        raise HTTPException(status_code=400, detail="A task is already running.")
        
    try:
        telegram_link_service.start_update(
            library_id=lib["id"], 
            target_channel=lib["telegram_channel"], 
            background_tasks=background_tasks
        )
        return {"status": "started", "mode": "update_links"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/task-status")
async def get_task_status():
    """Returns the current status of the running task."""
    if library_import_service.is_running():
        return library_import_service.get_status()
    elif telegram_link_service.is_running():
        return telegram_link_service.get_status()
        
    # If neither is running, return the most recently completed one, or default to link service
    if library_import_service.progress.status != "idle" and library_import_service.progress.end_time > telegram_link_service.progress.end_time:
        return library_import_service.get_status()
        
    return telegram_link_service.get_status()
