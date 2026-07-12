from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.database import MovieQueries
from backend.models import LibraryListResponse, LibraryResponse

router = APIRouter(prefix="/api", tags=["libraries"])


def _get_queries(request: Request) -> MovieQueries:
    return request.app.state.queries  # type: ignore[return-value]


@router.get("/libraries", response_model=LibraryListResponse)
def list_libraries(
    queries: MovieQueries = Depends(_get_queries),
) -> LibraryListResponse:
    """Return all active libraries with movie counts."""
    return LibraryListResponse(libraries=queries.get_libraries())


@router.get("/libraries/{slug}", response_model=LibraryResponse)
def get_library(
    slug: str,
    queries: MovieQueries = Depends(_get_queries),
) -> LibraryResponse:
    """Return a single library by slug."""
    lib = queries.get_library_by_slug(slug)
    if lib is None:
        raise HTTPException(status_code=404, detail="Library not found")
    return LibraryResponse(**lib)
