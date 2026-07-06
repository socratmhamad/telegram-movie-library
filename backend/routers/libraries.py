from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from backend.database import MovieQueries

router = APIRouter(prefix="/api/libraries", tags=["libraries"])

def _get_queries(request: Request) -> MovieQueries:
    return request.app.state.queries  # type: ignore[return-value]

class LibraryCreateRequest(BaseModel):
    name: str
    telegram_channel: str
    telegram_channel_id: str | None = None

@router.get("")
def list_libraries(queries: MovieQueries = Depends(_get_queries)):
    return {"libraries": queries.get_libraries()}

@router.get("/{library_slug}")
def get_library(library_slug: str, queries: MovieQueries = Depends(_get_queries)):
    lib = queries.get_library_by_slug(library_slug)
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    return lib

@router.post("")
def create_library(req: LibraryCreateRequest, queries: MovieQueries = Depends(_get_queries)):
    # We should add a method to create library in database.py
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', req.name.lower()).strip('-')
    
    with queries._get_session() as session:
        from database.models import Library
        from sqlalchemy import select
        
        # Check if slug exists
        if session.execute(select(Library).where(Library.slug == slug)).scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Library with similar name already exists.")
            
        lib = Library(
            name=req.name,
            slug=slug,
            telegram_channel=req.telegram_channel,
            telegram_channel_id=req.telegram_channel_id
        )
        session.add(lib)
        session.commit()
        
        return {
            "id": lib.id,
            "name": lib.name,
            "slug": lib.slug,
            "telegram_channel": lib.telegram_channel,
            "telegram_channel_id": lib.telegram_channel_id,
            "is_active": lib.is_active,
            "last_scan": None,
            "last_migration": None,
        }

class LibraryUpdateRequest(BaseModel):
    name: str
    slug: str
    telegram_channel: str
    telegram_channel_id: str | None = None
    is_active: bool

@router.patch("/{library_slug}")
def update_library(library_slug: str, req: LibraryUpdateRequest, queries: MovieQueries = Depends(_get_queries)):
    try:
        updated = queries.update_library(
            old_slug=library_slug,
            name=req.name,
            slug=req.slug,
            telegram_channel=req.telegram_channel,
            telegram_channel_id=req.telegram_channel_id,
            is_active=req.is_active
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Library not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
