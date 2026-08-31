from __future__ import annotations

import json
import math
from typing import Any

from sqlalchemy import select, func, distinct, case, and_
from sqlalchemy.orm import Session

from database.models import init_db
from database.tv_models import TVLibrary, TVSeries, TMDBTVSeries, FeaturedTVSeries

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"


class SeriesQueries:
    """Read-only query layer for TV series and libraries."""

    def __init__(self, database_url: str) -> None:
        self.SessionLocal = init_db(database_url)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    # ------------------------------------------------------------------
    # TV Library queries
    # ------------------------------------------------------------------

    def get_tv_libraries(self) -> list[dict[str, Any]]:
        with self._get_session() as session:
            libs = session.execute(
                select(TVLibrary).order_by(TVLibrary.display_order.asc(), TVLibrary.id.asc())
            ).scalars().all()

            result = []
            for lib in libs:
                series_count = session.scalar(
                    select(func.count(TVSeries.id)).where(TVSeries.library_id == lib.id)
                ) or 0
                poster_paths = session.scalars(
                    select(TMDBTVSeries.poster_path)
                    .join(TVSeries, TVSeries.tmdb_tv_id == TMDBTVSeries.id)
                    .where(TVSeries.library_id == lib.id)
                    .where(TMDBTVSeries.poster_path != None)
                    .where(TMDBTVSeries.poster_path != "")
                    .limit(5)
                ).all()
                posters = [f"{TMDB_IMAGE_BASE}/w500{path}" for path in poster_paths if path]

                result.append({
                    "id": lib.id,
                    "name": lib.name,
                    "name_en": lib.name_en,
                    "slug": lib.slug,
                    "telegram_channel": lib.telegram_channel,
                    "is_active": lib.is_active if lib.is_active is not None else True,
                    "series_count": series_count,
                    "posters": posters,
                    "display_order": lib.display_order if lib.display_order is not None else 0,
                })
            return result

    def get_tv_library_by_slug(self, slug: str) -> dict[str, Any] | None:
        with self._get_session() as session:
            lib = session.execute(
                select(TVLibrary).where(TVLibrary.slug == slug)
            ).scalar_one_or_none()
            if lib is None:
                return None
            series_count = session.scalar(
                select(func.count(TVSeries.id)).where(TVSeries.library_id == lib.id)
            ) or 0
            poster_paths = session.scalars(
                select(TMDBTVSeries.poster_path)
                .join(TVSeries, TVSeries.tmdb_tv_id == TMDBTVSeries.id)
                .where(TVSeries.library_id == lib.id)
                .where(TMDBTVSeries.poster_path != None)
                .where(TMDBTVSeries.poster_path != "")
                .limit(5)
            ).all()
            posters = [f"{TMDB_IMAGE_BASE}/w500{path}" for path in poster_paths if path]

            return {
                "id": lib.id,
                "name": lib.name,
                "name_en": lib.name_en,
                "slug": lib.slug,
                "telegram_channel": lib.telegram_channel,
                "is_active": lib.is_active if lib.is_active is not None else True,
                "series_count": series_count,
                "posters": posters,
                "display_order": lib.display_order if lib.display_order is not None else 0,
            }

    # ------------------------------------------------------------------
    # Series list (paginated, searchable, filterable, sortable)
    # ------------------------------------------------------------------

    def get_series(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        genre: str | None = None,
        sort_by: str = "title",
        sort_order: str = "asc",
        library_id: int | None = None,
    ) -> dict[str, Any]:
        _VALID_SORT_COLUMNS: dict[str, Any] = {
            "title": TVSeries.title,
            "first_air_date": TMDBTVSeries.first_air_date,
            "vote_average": TMDBTVSeries.vote_average,
        }
        sort_column = _VALID_SORT_COLUMNS.get(sort_by, TVSeries.title)
        sort_order_col = sort_column.desc()

        with self._get_session() as session:
            if library_id is not None:
                lib = session.scalar(select(TVLibrary).where(TVLibrary.id == library_id))
                if lib and lib.is_active == False:
                    return {
                        "items": [],
                        "total": 0,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": 0,
                    }

            # Base query
            query = select(TVSeries, TMDBTVSeries).outerjoin(
                TMDBTVSeries, TVSeries.tmdb_tv_id == TMDBTVSeries.id
            )

            if library_id is not None:
                query = query.where(TVSeries.library_id == library_id)

            if search:
                query = query.where(TVSeries.title.ilike(f"%{search}%"))

            if genre:
                query = query.where(TMDBTVSeries.genres.ilike(f'%"{genre}"%'))

            count_query = select(func.count()).select_from(query.subquery())
            total = session.scalar(count_query) or 0

            offset = (page - 1) * page_size

            has_poster_case = case(
                (and_(TMDBTVSeries.poster_path.isnot(None), TMDBTVSeries.poster_path != ""), 1),
                else_=0
            ).desc()

            query = query.order_by(has_poster_case, sort_order_col).limit(page_size).offset(offset)

            rows = session.execute(query).all()

            items: list[dict[str, Any]] = []
            for series, tmdb in rows:
                poster_url = None
                genres = []
                first_air_date = None
                vote_average = None
                number_of_seasons = None

                if tmdb:
                    poster_path = tmdb.poster_path
                    if poster_path:
                        poster_url = f"{TMDB_IMAGE_BASE}/w500{poster_path}"

                    first_air_date = tmdb.first_air_date
                    vote_average = tmdb.vote_average
                    number_of_seasons = tmdb.number_of_seasons

                    genres_raw = tmdb.genres
                    if genres_raw:
                        try:
                            genres = json.loads(genres_raw)
                        except (json.JSONDecodeError, TypeError):
                            pass

                items.append(
                    {
                        "id": series.id,
                        "title": series.title,
                        "poster_url": poster_url,
                        "first_air_date": first_air_date,
                        "vote_average": vote_average,
                        "genres": genres,
                        "number_of_seasons": number_of_seasons,
                    }
                )

            total_pages = math.ceil(total / page_size) if page_size > 0 else 0

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }

    # ------------------------------------------------------------------
    # Single series detail
    # ------------------------------------------------------------------

    def get_series_detail(self, series_id: int, language: str | None = None) -> dict[str, Any] | None:
        with self._get_session() as session:
            series = session.execute(
                select(TVSeries).where(TVSeries.id == series_id)
            ).scalar_one_or_none()

            if series is None:
                return None

            tmdb = None
            if series.tmdb_tv_id:
                tmdb_row = session.execute(
                    select(TMDBTVSeries).where(TMDBTVSeries.id == series.tmdb_tv_id)
                ).scalar_one_or_none()

                if tmdb_row:
                    overview = tmdb_row.overview
                    genres_raw = tmdb_row.genres
                    genres: list[str] = []
                    if genres_raw:
                        try:
                            parsed = json.loads(genres_raw) if isinstance(genres_raw, str) else genres_raw
                            if isinstance(parsed, list):
                                genres = parsed
                        except (json.JSONDecodeError, TypeError):
                            genres = []

                    if language == "ar":
                        try:
                            if tmdb_row.tmdb_id:
                                from tmdb_tv_service import get_tv_details
                                details = get_tv_details(int(tmdb_row.tmdb_id), language="ar")
                                if details.get("overview") and details["overview"].strip():
                                    overview = details["overview"].strip()
                                if details.get("genres"):
                                    genres = details["genres"] if isinstance(details["genres"], list) else []
                        except Exception as e:
                            print(f"Warning: Failed to fetch Arabic TV metadata: {e}")

                    tmdb = {
                        "id": tmdb_row.id,
                        "tmdb_id": tmdb_row.tmdb_id,
                        "name": tmdb_row.name,
                        "original_name": tmdb_row.original_name,
                        "overview": overview,
                        "poster_path": tmdb_row.poster_path,
                        "backdrop_path": tmdb_row.backdrop_path,
                        "first_air_date": tmdb_row.first_air_date,
                        "vote_average": tmdb_row.vote_average,
                        "number_of_seasons": tmdb_row.number_of_seasons,
                        "number_of_episodes": tmdb_row.number_of_episodes,
                        "genres": genres,
                        "status": tmdb_row.status,
                    }

            return {
                "id": series.id,
                "title": series.title,
                "telegram_channel_link": series.telegram_channel_link,
                "tmdb": tmdb,
            }

    # ------------------------------------------------------------------
    # Genres
    # ------------------------------------------------------------------

    def get_genres(self, *, library_id: int | None = None) -> list[str]:
        with self._get_session() as session:
            genre_query = (
                select(distinct(TMDBTVSeries.genres))
                .where(TMDBTVSeries.genres.isnot(None))
                .where(TMDBTVSeries.genres != '[]')
            )
            if library_id is not None:
                genre_query = genre_query.join(TVSeries, TVSeries.tmdb_tv_id == TMDBTVSeries.id).where(TVSeries.library_id == library_id)

            rows = session.execute(genre_query).scalars().all()

            all_genres: set[str] = set()
            for genres_raw in rows:
                if not genres_raw:
                    continue
                try:
                    parsed = json.loads(genres_raw)
                    if isinstance(parsed, list):
                        all_genres.update(parsed)
                except (json.JSONDecodeError, TypeError):
                    continue

            return sorted(all_genres)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self, *, library_id: int | None = None) -> dict[str, Any]:
        with self._get_session() as session:
            total_filter = select(func.count(TVSeries.id))
            if library_id is not None:
                total_filter = total_filter.where(TVSeries.library_id == library_id)
            total = session.scalar(total_filter) or 0

            tmdb_filter = select(func.count(TVSeries.id)).where(TVSeries.tmdb_tv_id.isnot(None))
            if library_id is not None:
                tmdb_filter = tmdb_filter.where(TVSeries.library_id == library_id)
            with_tmdb = session.scalar(tmdb_filter) or 0

            return {
                "total_series": total,
                "series_with_tmdb": with_tmdb,
                "series_without_tmdb": total - with_tmdb,
            }

    # ------------------------------------------------------------------
    # Featured TV Series queries
    # ------------------------------------------------------------------

    def get_featured_tv_series(self) -> list[dict[str, Any]]:
        with self._get_session() as session:
            rows = session.execute(
                select(FeaturedTVSeries).order_by(FeaturedTVSeries.created_at.desc(), FeaturedTVSeries.id.desc())
            ).scalars().all()
            return [
                {
                    "id": row.id,
                    "title": row.title,
                    "poster_url": row.poster_url,
                    "telegram_channel_link": row.telegram_channel_link,
                    "description": row.description,
                    "category": row.category or "Trending",
                }
                for row in rows
            ]

    def get_featured_tv_series_by_id(self, item_id: int) -> dict[str, Any] | None:
        with self._get_session() as session:
            row = session.execute(
                select(FeaturedTVSeries).where(FeaturedTVSeries.id == item_id)
            ).scalar_one_or_none()
            if row is None:
                return None
            return {
                "id": row.id,
                "title": row.title,
                "poster_url": row.poster_url,
                "telegram_channel_link": row.telegram_channel_link,
                "description": row.description,
                "category": row.category or "Trending",
            }

    def create_featured_tv_series(self, data: dict[str, Any]) -> dict[str, Any]:
        with self._get_session() as session:
            entry = FeaturedTVSeries(
                title=data["title"],
                poster_url=data["poster_url"],
                telegram_channel_link=data["telegram_channel_link"],
                description=data.get("description"),
                category=data.get("category") or "Trending",
            )
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return {
                "id": entry.id,
                "title": entry.title,
                "poster_url": entry.poster_url,
                "telegram_channel_link": entry.telegram_channel_link,
                "description": entry.description,
                "category": entry.category,
            }

    def update_featured_tv_series(self, item_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        with self._get_session() as session:
            entry = session.execute(
                select(FeaturedTVSeries).where(FeaturedTVSeries.id == item_id)
            ).scalar_one_or_none()
            if entry is None:
                return None
            if "title" in data and data["title"] is not None:
                entry.title = data["title"]
            if "poster_url" in data and data["poster_url"] is not None:
                entry.poster_url = data["poster_url"]
            if "telegram_channel_link" in data and data["telegram_channel_link"] is not None:
                entry.telegram_channel_link = data["telegram_channel_link"]
            if "description" in data:
                entry.description = data["description"]
            if "category" in data and data["category"] is not None:
                entry.category = data["category"]
            session.commit()
            session.refresh(entry)
            return {
                "id": entry.id,
                "title": entry.title,
                "poster_url": entry.poster_url,
                "telegram_channel_link": entry.telegram_channel_link,
                "description": entry.description,
                "category": entry.category,
            }

    def delete_featured_tv_series(self, item_id: int) -> bool:
        with self._get_session() as session:
            entry = session.execute(
                select(FeaturedTVSeries).where(FeaturedTVSeries.id == item_id)
            ).scalar_one_or_none()
            if entry is None:
                return False
            session.delete(entry)
            session.commit()
            return True
