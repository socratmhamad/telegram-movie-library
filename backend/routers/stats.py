from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request

from backend.database import MovieQueries
from backend.models import StatsResponse

router = APIRouter(prefix="/api", tags=["stats"])


def _get_queries(request: Request) -> MovieQueries:
    return request.app.state.queries  # type: ignore[return-value]


@router.get("/stats", response_model=StatsResponse)
def library_stats(
    library_id: int | None = Query(None, description="Filter stats by library ID"),
    queries: MovieQueries = Depends(_get_queries),
) -> StatsResponse:
    """Return aggregate library statistics and genre breakdown."""
    return StatsResponse(**queries.get_stats(library_id=library_id))

