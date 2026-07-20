from __future__ import annotations

import json
import math
import os
from typing import Any

from sqlalchemy import select, func, distinct, case, and_
from sqlalchemy.orm import Session, joinedload


from database.models import init_db, Library, Movie, TMDBMovie, TelegramMessage

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

    def get_libraries(self) -> list[dict[str, Any]]:
        with self._get_session() as session:
            libs = session.execute(
                select(Library).where(Library.is_active == True).order_by(Library.id)
            ).scalars().all()

            result = []
            for lib in libs:
                movie_count = session.scalar(
                    select(func.count(Movie.id)).where(Movie.library_id == lib.id)
                ) or 0
                poster_paths = session.scalars(
                    select(TMDBMovie.poster_path)
                    .join(Movie, Movie.tmdb_movie_id == TMDBMovie.id)
                    .where(Movie.library_id == lib.id)
                    .where(TMDBMovie.poster_path != None)
                    .where(TMDBMovie.poster_path != "")
                    .limit(5)
                ).all()
                posters = [f"{TMDB_IMAGE_BASE}/w500{path}" for path in poster_paths if path]

                result.append({
                    "id": lib.id,
                    "name": lib.name,
                    "slug": lib.slug,
                    "telegram_channel": lib.telegram_channel,
                    "movie_count": movie_count,
                    "posters": posters,
                })
            return result

    def get_library_by_slug(self, slug: str) -> dict[str, Any] | None:
        with self._get_session() as session:
            lib = session.execute(
                select(Library).where(Library.slug == slug)
            ).scalar_one_or_none()
            if lib is None:
                return None
            movie_count = session.scalar(
                select(func.count(Movie.id)).where(Movie.library_id == lib.id)
            ) or 0
            poster_paths = session.scalars(
                select(TMDBMovie.poster_path)
                .join(Movie, Movie.tmdb_movie_id == TMDBMovie.id)
                .where(Movie.library_id == lib.id)
                .where(TMDBMovie.poster_path != None)
                .where(TMDBMovie.poster_path != "")
                .limit(5)
            ).all()
            posters = [f"{TMDB_IMAGE_BASE}/w500{path}" for path in poster_paths if path]

            return {
                "id": lib.id,
                "name": lib.name,
                "slug": lib.slug,
                "telegram_channel": lib.telegram_channel,
                "movie_count": movie_count,
                "posters": posters,
            }

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
        library_id: int | None = None,
    ) -> dict[str, Any]:
        sort_column = _VALID_SORT_COLUMNS.get(sort_by, Movie.title)
        sort_order_col = sort_column.desc()

        with self._get_session() as session:
            # Base query
            query = select(Movie, TMDBMovie).outerjoin(TMDBMovie, Movie.tmdb_movie_id == TMDBMovie.id)

            if library_id is not None:
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
            
            # Prioritize movies with posters first
            has_poster_case = case(
                (and_(TMDBMovie.poster_path.isnot(None), TMDBMovie.poster_path != ""), 1),
                else_=0
            ).desc()
            
            query = query.order_by(has_poster_case, sort_order_col).limit(page_size).offset(offset)
            
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

    def get_movie(self, movie_id: int, language: str | None = None) -> dict[str, Any] | None:
        with self._get_session() as session:
            movie = session.execute(
                select(Movie)
                .options(joinedload(Movie.tmdb_movie), joinedload(Movie.library))
                .where(Movie.id == movie_id)
            ).scalar_one_or_none()

            if movie is None:
                return None

            tmdb = None
            if movie.tmdb_movie:
                tmdb_movie = movie.tmdb_movie
                overview = tmdb_movie.overview
                genres_raw = tmdb_movie.genres
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
                        if tmdb_movie.tmdb_id:
                            from tmdb_service import get_movie_details
                            details = get_movie_details(int(tmdb_movie.tmdb_id), language="ar")
                            if details.get("overview") and details["overview"].strip():
                                overview = details["overview"].strip()
                            if details.get("genres"):
                                genres = details["genres"] if isinstance(details["genres"], list) else []
                    except Exception as e:
                        print(f"Warning: Failed to fetch Arabic metadata: {e}")

                tmdb = {
                    "id": tmdb_movie.id,
                    "tmdb_id": tmdb_movie.tmdb_id,
                    "title": tmdb_movie.title,
                    "original_title": tmdb_movie.original_title,
                    "overview": overview,
                    "poster_path": tmdb_movie.poster_path,
                    "backdrop_path": tmdb_movie.backdrop_path,
                    "release_date": tmdb_movie.release_date,
                    "vote_average": tmdb_movie.vote_average,
                    "runtime": tmdb_movie.runtime,
                    "genres": genres,
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
            if telegram_messages:
                first_msg_id = telegram_messages[0]["message_id"]
                library = movie.library
                if library and library.telegram_channel_id:
                    telegram_link = f"https://t.me/c/{library.telegram_channel_id}/{first_msg_id}"
                elif library and library.telegram_channel:
                    # Public channel: extract username from URL or use handle directly
                    channel = library.telegram_channel
                    if channel.startswith("@"):
                        channel = channel[1:]
                    elif "t.me/" in channel:
                        channel = channel.split("t.me/")[-1].strip("/")
                    if channel and not channel.startswith("+"):
                        telegram_link = f"https://t.me/{channel}/{first_msg_id}"

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

    def get_genres(self, *, library_id: int | None = None) -> list[str]:
        with self._get_session() as session:
            genre_query = (
                select(distinct(TMDBMovie.genres))
                .where(TMDBMovie.genres.isnot(None))
                .where(TMDBMovie.genres != '[]')
            )
            if library_id is not None:
                genre_query = genre_query.join(Movie, Movie.tmdb_movie_id == TMDBMovie.id).where(Movie.library_id == library_id)
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
    # Library statistics
    # ------------------------------------------------------------------

    def get_stats(self, *, library_id: int | None = None) -> dict[str, Any]:
        with self._get_session() as session:
            movie_filter = select(func.count(Movie.id))
            if library_id is not None:
                movie_filter = movie_filter.where(Movie.library_id == library_id)
            total_movies = session.scalar(movie_filter) or 0

            tmdb_filter = select(func.count(Movie.id)).where(Movie.tmdb_movie_id.isnot(None))
            if library_id is not None:
                tmdb_filter = tmdb_filter.where(Movie.library_id == library_id)
            movies_with_tmdb = session.scalar(tmdb_filter) or 0
            
            movies_without_tmdb = total_movies - movies_with_tmdb

            msg_filter = select(func.count(TelegramMessage.id))
            if library_id is not None:
                msg_filter = msg_filter.join(Movie, TelegramMessage.movie_id == Movie.id).where(Movie.library_id == library_id)
            total_messages = session.scalar(msg_filter) or 0

            # Genre breakdown
            genre_query = (
                select(TMDBMovie.genres)
                .where(TMDBMovie.genres.isnot(None))
                .where(TMDBMovie.genres != '[]')
            )
            if library_id is not None:
                genre_query = genre_query.join(Movie, Movie.tmdb_movie_id == TMDBMovie.id).where(Movie.library_id == library_id)
            genre_rows = session.execute(genre_query).scalars().all()

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
