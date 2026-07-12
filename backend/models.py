from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, computed_field, field_validator


TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_genres(value: Any) -> list[str]:
    """Accept a JSON string or a plain list and always return ``list[str]``."""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, TypeError):
            return []
    return []


# ---------------------------------------------------------------------------
# TMDB
# ---------------------------------------------------------------------------

class TmdbMovieResponse(BaseModel):
    id: int
    tmdb_id: int
    title: str | None = None
    original_title: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    release_date: str | None = None
    vote_average: float | None = None
    runtime: int | None = None
    genres: list[str] = []
    imdb_id: str | None = None

    @field_validator("genres", mode="before")
    @classmethod
    def parse_genres(cls, value: Any) -> list[str]:
        return _parse_genres(value)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def poster_url(self) -> str | None:
        if not self.poster_path:
            return None
        return f"{TMDB_IMAGE_BASE}/w500{self.poster_path}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def backdrop_url(self) -> str | None:
        if not self.backdrop_path:
            return None
        return f"{TMDB_IMAGE_BASE}/original{self.backdrop_path}"


# ---------------------------------------------------------------------------
# Telegram messages
# ---------------------------------------------------------------------------

class TelegramMessageResponse(BaseModel):
    id: int
    movie_id: int
    message_id: int


# ---------------------------------------------------------------------------
# Movie detail (separate page, not modal)
# ---------------------------------------------------------------------------

class MovieDetailResponse(BaseModel):
    id: int
    title: str
    tmdb_movie_id: int | None = None
    tmdb: TmdbMovieResponse | None = None
    telegram_messages: list[TelegramMessageResponse] = []
    telegram_link: str | None = None


# ---------------------------------------------------------------------------
# Movie list item (lightweight for grid / list views)
# ---------------------------------------------------------------------------

class MovieListItem(BaseModel):
    id: int
    title: str
    poster_url: str | None = None
    release_date: str | None = None
    vote_average: float | None = None
    genres: list[str] = []
    runtime: int | None = None

    @field_validator("genres", mode="before")
    @classmethod
    def parse_genres(cls, value: Any) -> list[str]:
        return _parse_genres(value)


# ---------------------------------------------------------------------------
# Paginated wrapper
# ---------------------------------------------------------------------------

class PaginatedResponse(BaseModel):
    items: list[MovieListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------------------
# Genres
# ---------------------------------------------------------------------------

class GenreListResponse(BaseModel):
    genres: list[str]


# ---------------------------------------------------------------------------
# Library statistics
# ---------------------------------------------------------------------------

class StatsResponse(BaseModel):
    total_movies: int
    movies_with_tmdb: int
    movies_without_tmdb: int
    total_messages: int
    genres_breakdown: dict[str, int]


# ---------------------------------------------------------------------------
# Library
# ---------------------------------------------------------------------------

class LibraryResponse(BaseModel):
    id: int
    name: str
    slug: str
    telegram_channel: str | None = None
    movie_count: int = 0


class LibraryListResponse(BaseModel):
    libraries: list[LibraryResponse]

