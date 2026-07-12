from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.database import MovieQueries
from backend.models import (
    GenreListResponse,
    MovieDetailResponse,
    PaginatedResponse,
)

router = APIRouter(prefix="/api", tags=["movies"])


def _get_queries(request: Request) -> MovieQueries:
    return request.app.state.queries  # type: ignore[return-value]


@router.get("/movies", response_model=PaginatedResponse)
def list_movies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search movies by title (case-insensitive partial match)"),
    genre: str | None = Query(None, description="Filter by genre name"),
    sort_by: str = Query(
        "title",
        description="Sort field",
        pattern="^(title|release_date|vote_average|runtime)$",
    ),
    sort_order: str = Query(
        "asc",
        description="Sort direction",
        pattern="^(asc|desc)$",
    ),
    library_id: int | None = Query(None, description="Filter by library ID"),
    queries: MovieQueries = Depends(_get_queries),
) -> PaginatedResponse:
    """Return a paginated list of movies with lightweight TMDB metadata."""
    result = queries.get_movies(
        page=page,
        page_size=page_size,
        search=search,
        genre=genre,
        sort_by=sort_by,
        sort_order=sort_order,
        library_id=library_id,
    )
    return PaginatedResponse(**result)


@router.get("/movies/{movie_id}", response_model=MovieDetailResponse)
def get_movie(
    movie_id: int,
    queries: MovieQueries = Depends(_get_queries),
) -> MovieDetailResponse:
    """Return full details for a single movie (detail page, not modal)."""
    movie = queries.get_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return MovieDetailResponse(**movie)


@router.get("/genres", response_model=GenreListResponse)
def list_genres(
    library_id: int | None = Query(None, description="Filter genres by library ID"),
    queries: MovieQueries = Depends(_get_queries),
) -> GenreListResponse:
    """Return a sorted list of every unique genre in the library."""
    return GenreListResponse(genres=queries.get_genres(library_id=library_id))

