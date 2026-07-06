from __future__ import annotations

import json
import math
from typing import Any

from sqlalchemy import select, func, distinct, case
from sqlalchemy.orm import Session

from database.models import init_db, Movie, TMDBMovie, TelegramMessage

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

_VALID_SORT_COLUMNS: dict[str, Any] = {
    "title": Movie.title,
    "release_date": TMDBMovie.release_date,
    "vote_average": TMDBMovie.vote_average,
    "runtime": TMDBMovie.runtime,
}

class MovieQueries:
    """Read-only query layer that powers the FastAPI endpoints.

    Uses SQLAlchemy.
    Each public method opens (and closes) its own connection so the
    FastAPI thread-pool can serve requests concurrently.
    """

    def __init__(self, database_url: str) -> None:
        self.SessionLocal = init_db(database_url)

    # ------------------------------------------------------------------
    # Connection helper
    # ------------------------------------------------------------------

    def _get_session(self) -> Session:
        return self.SessionLocal()

    # ------------------------------------------------------------------
    # Movie list (paginated, searchable, filterable, sortable)
    # ------------------------------------------------------------------

    def get_movies(
        self,
        library_id: int,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        genre: str | None = None,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        sort_column = _VALID_SORT_COLUMNS.get(sort_by, Movie.title)
        
        if sort_order.lower() == "desc":
            sort_order_col = sort_column.desc()
        else:
            sort_order_col = sort_column.asc()

        with self._get_session() as session:
            # Base query
            query = select(Movie, TMDBMovie).outerjoin(TMDBMovie, Movie.tmdb_movie_id == TMDBMovie.id)
            query = query.where(Movie.library_id == library_id)

            if search:
                query = query.where(Movie.title.ilike(f"%{search}%"))

            if genre:
                query = query.where(TMDBMovie.genres.ilike(f'%"{genre}"%'))

            # Count total
            count_query = select(func.count()).select_from(query.subquery())
            total = session.scalar(count_query) or 0

            # Paginated rows
            offset = (page - 1) * page_size
            query = query.order_by(sort_order_col).limit(page_size).offset(offset)
            
            rows = session.execute(query).all()

            items: list[dict[str, Any]] = []
            for movie, tmdb in rows:
                poster_url = None
                genres = []
                release_date = None
                vote_average = None
                runtime = None

                if tmdb:
                    poster_path = tmdb.poster_path
                    if poster_path:
                        poster_url = f"{TMDB_IMAGE_BASE}/w500{poster_path}"
                    
                    release_date = tmdb.release_date
                    vote_average = tmdb.vote_average
                    runtime = tmdb.runtime

                    genres_raw = tmdb.genres
                    if genres_raw:
                        try:
                            genres = json.loads(genres_raw)
                        except (json.JSONDecodeError, TypeError):
                            pass

                items.append(
                    {
                        "id": movie.id,
                        "title": movie.title,
                        "poster_url": poster_url,
                        "release_date": release_date,
                        "vote_average": vote_average,
                        "genres": genres,
                        "runtime": runtime,
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
    # Single movie detail
    # ------------------------------------------------------------------

    def get_movie(self, library_id: int, movie_id: int) -> dict[str, Any] | None:
        with self._get_session() as session:
            movie = session.execute(
                select(Movie).where(Movie.id == movie_id, Movie.library_id == library_id)
            ).scalar_one_or_none()

            if movie is None:
                return None

            tmdb = None
            if movie.tmdb_movie:
                tmdb_movie = movie.tmdb_movie
                tmdb = {
                    "id": tmdb_movie.id,
                    "tmdb_id": tmdb_movie.tmdb_id,
                    "title": tmdb_movie.title,
                    "original_title": tmdb_movie.original_title,
                    "overview": tmdb_movie.overview,
                    "poster_path": tmdb_movie.poster_path,
                    "backdrop_path": tmdb_movie.backdrop_path,
                    "release_date": tmdb_movie.release_date,
                    "vote_average": tmdb_movie.vote_average,
                    "runtime": tmdb_movie.runtime,
                    "genres": tmdb_movie.genres,
                    "imdb_id": tmdb_movie.imdb_id,
                }

            messages = session.execute(
                select(TelegramMessage)
                .where(TelegramMessage.movie_id == movie_id)
                .order_by(TelegramMessage.message_id)
            ).scalars().all()

            telegram_messages = [
                {
                    "id": msg.id,
                    "movie_id": msg.movie_id,
                    "message_id": msg.message_id,
                    "quality": getattr(msg, "quality", None),
                    "codec": getattr(msg, "codec", None),
                    "release_type": getattr(msg, "release_type", None),
                    "file_size": getattr(msg, "file_size", None),
                    "language": getattr(msg, "language", None),
                }
                for msg in messages
            ]

            telegram_link = None
            if telegram_messages:
                # We need the library to get telegram_channel_id
                from database.models import Library
                library = session.execute(select(Library).where(Library.id == movie.library_id)).scalar_one_or_none()
                channel_id = library.telegram_channel_id if library else None
                
                if channel_id:
                    first_msg_id = telegram_messages[0]["message_id"]
                    telegram_link = f"https://t.me/c/{channel_id}/{first_msg_id}"
                elif library and library.telegram_channel.startswith('@'):
                    public_name = library.telegram_channel[1:]
                    first_msg_id = telegram_messages[0]["message_id"]
                    telegram_link = f"https://t.me/{public_name}/{first_msg_id}"

            return {
                "id": movie.id,
                "title": movie.title,
                "tmdb_movie_id": movie.tmdb_movie_id,
                "tmdb": tmdb,
                "telegram_messages": telegram_messages,
                "telegram_link": telegram_link,
            }

    # ------------------------------------------------------------------
    # Distinct genre list
    # ------------------------------------------------------------------

    def get_genres(self, library_id: int) -> list[str]:
        with self._get_session() as session:
            rows = session.execute(
                select(distinct(TMDBMovie.genres))
                .join(Movie, Movie.tmdb_movie_id == TMDBMovie.id)
                .where(Movie.library_id == library_id)
                .where(TMDBMovie.genres.isnot(None))
                .where(TMDBMovie.genres != '[]')
            ).scalars().all()

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
    # Library statistics
    # ------------------------------------------------------------------

    def get_stats(self, library_id: int) -> dict[str, Any]:
        with self._get_session() as session:
            total_movies = session.scalar(select(func.count(Movie.id)).where(Movie.library_id == library_id)) or 0
            
            movies_with_tmdb = session.scalar(
                select(func.count(Movie.id))
                .where(Movie.library_id == library_id)
                .where(Movie.tmdb_movie_id.isnot(None))
            ) or 0
            
            movies_without_tmdb = total_movies - movies_with_tmdb
            
            total_messages = session.scalar(
                select(func.count(TelegramMessage.id))
                .join(Movie, TelegramMessage.movie_id == Movie.id)
                .where(Movie.library_id == library_id)
            ) or 0

            # Genre breakdown
            genre_rows = session.execute(
                select(TMDBMovie.genres)
                .join(Movie, Movie.tmdb_movie_id == TMDBMovie.id)
                .where(Movie.library_id == library_id)
                .where(TMDBMovie.genres.isnot(None))
                .where(TMDBMovie.genres != '[]')
            ).scalars().all()

            genre_counts: dict[str, int] = {}
            for genres_raw in genre_rows:
                if not genres_raw:
                    continue
                try:
                    parsed = json.loads(genres_raw)
                    if isinstance(parsed, list):
                        for genre in parsed:
                            genre_counts[genre] = genre_counts.get(genre, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue

            return {
                "total_movies": total_movies,
                "movies_with_tmdb": movies_with_tmdb,
                "movies_without_tmdb": movies_without_tmdb,
                "total_messages": total_messages,
                "genres_breakdown": dict(
                    sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
                ),
            }

    # ------------------------------------------------------------------
    # Libraries
    # ------------------------------------------------------------------
    
    from database.models import Library
    
    def get_libraries(self) -> list[dict[str, Any]]:
        from database.models import Library
        with self._get_session() as session:
            rows = session.execute(select(Library)).scalars().all()
            return [
                {
                    "id": lib.id,
                    "name": lib.name,
                    "slug": lib.slug,
                    "telegram_channel": lib.telegram_channel,
                    "telegram_channel_id": lib.telegram_channel_id,
                    "is_active": lib.is_active,
                    "last_scan": lib.last_scan.isoformat() if lib.last_scan else None,
                    "last_migration": lib.last_migration.isoformat() if lib.last_migration else None,
                }
                for lib in rows
            ]
            
    def get_library_by_slug(self, slug: str) -> dict[str, Any] | None:
        from database.models import Library
        with self._get_session() as session:
            lib = session.execute(select(Library).where(Library.slug == slug)).scalar_one_or_none()
            if not lib:
                return None
            return {
                "id": lib.id,
                "name": lib.name,
                "slug": lib.slug,
                "telegram_channel": lib.telegram_channel,
                "telegram_channel_id": lib.telegram_channel_id,
                "is_active": lib.is_active,
                "last_scan": lib.last_scan.isoformat() if lib.last_scan else None,
                "last_migration": lib.last_migration.isoformat() if lib.last_migration else None,
            }

    def update_library(self, old_slug: str, name: str, slug: str, telegram_channel: str, telegram_channel_id: str | None, is_active: bool) -> dict[str, Any] | None:
        from database.models import Library
        with self._get_session() as session:
            lib = session.execute(select(Library).where(Library.slug == old_slug)).scalar_one_or_none()
            if not lib:
                return None
            
            # Check slug collision if changed
            if slug != old_slug:
                existing = session.execute(select(Library).where(Library.slug == slug)).scalar_one_or_none()
                if existing:
                    raise ValueError(f"A library with slug '{slug}' already exists.")
            
            lib.name = name
            lib.slug = slug
            lib.telegram_channel = telegram_channel
            lib.telegram_channel_id = telegram_channel_id
            lib.is_active = is_active
            
            session.commit()
            session.refresh(lib)
            
            return {
                "id": lib.id,
                "name": lib.name,
                "slug": lib.slug,
                "telegram_channel": lib.telegram_channel,
                "telegram_channel_id": lib.telegram_channel_id,
                "is_active": lib.is_active,
                "last_scan": lib.last_scan.isoformat() if lib.last_scan else None,
                "last_migration": lib.last_migration.isoformat() if lib.last_migration else None,
            }

    # ------------------------------------------------------------------
    # Featured movies (for homepage hero)
    # ------------------------------------------------------------------

    def get_featured_movies(self, limit: int = 8) -> list[dict[str, Any]]:
        """Return top-rated movies with backdrop images across all libraries.

        Used by the homepage hero carousel. Single DB query, no external calls.
        """
        with self._get_session() as session:
            query = (
                select(Movie, TMDBMovie)
                .join(TMDBMovie, Movie.tmdb_movie_id == TMDBMovie.id)
                .where(TMDBMovie.backdrop_path.isnot(None))
                .where(TMDBMovie.backdrop_path != '')
                .where(TMDBMovie.vote_average.isnot(None))
                .where(TMDBMovie.vote_average > 0)
                .order_by(TMDBMovie.vote_average.desc())
                .limit(limit)
            )

            rows = session.execute(query).all()

            items: list[dict[str, Any]] = []
            for movie, tmdb in rows:
                genres: list[str] = []
                if tmdb.genres:
                    try:
                        genres = json.loads(tmdb.genres)
                    except (json.JSONDecodeError, TypeError):
                        pass

                items.append({
                    "id": movie.id,
                    "title": movie.title,
                    "backdrop_url": f"{TMDB_IMAGE_BASE}/original{tmdb.backdrop_path}",
                    "poster_url": f"{TMDB_IMAGE_BASE}/w500{tmdb.poster_path}" if tmdb.poster_path else None,
                    "vote_average": tmdb.vote_average,
                    "release_date": tmdb.release_date,
                    "overview": tmdb.overview or "",
                    "genres": genres,
                    "runtime": tmdb.runtime,
                })

            return items
