from __future__ import annotations

import json
import math
from typing import Any

from sqlalchemy import select, func, distinct, case
from sqlalchemy.orm import Session

from backend.config import get_telegram_channel_id
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

    def get_movie(self, movie_id: int) -> dict[str, Any] | None:
        with self._get_session() as session:
            movie = session.execute(
                select(Movie).where(Movie.id == movie_id)
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
                }
                for msg in messages
            ]

            telegram_link = None
            channel_id = get_telegram_channel_id()
            if telegram_messages and channel_id:
                first_msg_id = telegram_messages[0]["message_id"]
                telegram_link = f"https://t.me/c/{channel_id}/{first_msg_id}"

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

    def get_genres(self) -> list[str]:
        with self._get_session() as session:
            rows = session.execute(
                select(distinct(TMDBMovie.genres))
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

    def get_stats(self) -> dict[str, Any]:
        with self._get_session() as session:
            total_movies = session.scalar(select(func.count(Movie.id))) or 0
            
            movies_with_tmdb = session.scalar(
                select(func.count(Movie.id)).where(Movie.tmdb_movie_id.isnot(None))
            ) or 0
            
            movies_without_tmdb = total_movies - movies_with_tmdb
            
            total_messages = session.scalar(select(func.count(TelegramMessage.id))) or 0

            # Genre breakdown
            genre_rows = session.execute(
                select(TMDBMovie.genres)
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
