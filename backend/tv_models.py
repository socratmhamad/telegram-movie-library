from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, computed_field, field_validator


TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"


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
# TV Library Schemas
# ---------------------------------------------------------------------------

class TVLibraryResponse(BaseModel):
    id: int
    name: str
    name_en: str | None = None
    slug: str
    telegram_channel: str | None = None
    is_active: bool = True
    series_count: int = 0
    posters: list[str] = []
    display_order: int = 0


class TVLibraryListResponse(BaseModel):
    libraries: list[TVLibraryResponse]


class TVLibraryCreateRequest(BaseModel):
    name: str
    name_en: str | None = None
    slug: str
    telegram_channel: str
    telegram_channel_id: str | None = None
    is_active: bool = True
    display_order: int | None = None


class TVLibraryUpdateRequest(BaseModel):
    name: str | None = None
    name_en: str | None = None
    slug: str | None = None
    telegram_channel: str | None = None
    telegram_channel_id: str | None = None
    is_active: bool | None = None
    display_order: int | None = None


class TVLibraryDetailResponse(BaseModel):
    id: int
    name: str
    name_en: str | None = None
    slug: str
    telegram_channel: str
    telegram_channel_id: str | None = None
    is_active: bool | None = None
    series_count: int = 0
    series_with_tmdb: int = 0
    series_without_tmdb: int = 0
    display_order: int = 0


class TVLibraryReorderRequest(BaseModel):
    items: list[dict[str, int]] | None = None
    ids: list[int] | None = None


# ---------------------------------------------------------------------------
# TMDB TV
# ---------------------------------------------------------------------------

class TmdbTVResponse(BaseModel):
    id: int
    tmdb_id: int
    name: str | None = None
    original_name: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    first_air_date: str | None = None
    vote_average: float | None = None
    number_of_seasons: int | None = None
    number_of_episodes: int | None = None
    genres: list[str] = []
    status: str | None = None

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
# Series detail
# ---------------------------------------------------------------------------

class SeriesDetailResponse(BaseModel):
    id: int
    title: str
    telegram_channel_link: str | None = None
    tmdb: TmdbTVResponse | None = None


# ---------------------------------------------------------------------------
# Series list item
# ---------------------------------------------------------------------------

class SeriesListItem(BaseModel):
    id: int
    title: str
    poster_url: str | None = None
    first_air_date: str | None = None
    vote_average: float | None = None
    genres: list[str] = []
    number_of_seasons: int | None = None

    @field_validator("genres", mode="before")
    @classmethod
    def parse_genres(cls, value: Any) -> list[str]:
        return _parse_genres(value)


# ---------------------------------------------------------------------------
# Paginated wrapper
# ---------------------------------------------------------------------------

class SeriesPaginatedResponse(BaseModel):
    items: list[SeriesListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------------------
# Genres
# ---------------------------------------------------------------------------

class SeriesGenreListResponse(BaseModel):
    genres: list[str]


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

class SeriesStatsResponse(BaseModel):
    total_series: int
    series_with_tmdb: int
    series_without_tmdb: int


# ---------------------------------------------------------------------------
# Featured TV Series
# ---------------------------------------------------------------------------

class FeaturedTVResponse(BaseModel):
    id: int
    title: str
    poster_url: str
    telegram_channel_link: str
    description: str | None = None
    category: str | None = "Trending"


class FeaturedTVListResponse(BaseModel):
    items: list[FeaturedTVResponse]


class FeaturedTVCreateRequest(BaseModel):
    title: str
    poster_url: str
    telegram_channel_link: str
    description: str | None = None
    category: str | None = "Trending"


class FeaturedTVUpdateRequest(BaseModel):
    title: str | None = None
    poster_url: str | None = None
    telegram_channel_link: str | None = None
    description: str | None = None
    category: str | None = None
