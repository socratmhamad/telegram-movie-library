from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.database import MovieQueries
from backend.models import StatsResponse

router = APIRouter(prefix="/api/libraries/{library_slug}", tags=["stats"])


def _get_queries(request: Request) -> MovieQueries:
    return request.app.state.queries  # type: ignore[return-value]


def _get_library_id(
    library_slug: str,
    queries: MovieQueries = Depends(_get_queries)
) -> int:
    lib = queries.get_library_by_slug(library_slug)
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    return lib["id"]


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    library_id: int = Depends(_get_library_id),
    queries: MovieQueries = Depends(_get_queries),
) -> StatsResponse:
    """Return high-level library statistics and genre breakdown."""
    return StatsResponse(**queries.get_stats(library_id))
