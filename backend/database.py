from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from typing import Any

from backend.config import get_telegram_channel_id

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

_VALID_SORT_COLUMNS: dict[str, str] = {
    "title": "m.title",
    "release_date": "t.release_date",
    "vote_average": "t.vote_average",
    "runtime": "t.runtime",
}


class MovieQueries:
    """Read-only query layer that powers the FastAPI endpoints.

    Uses raw ``sqlite3`` — no ORM — to keep the stack lightweight.
    Each public method opens (and closes) its own connection so the
    FastAPI thread-pool can serve requests concurrently.
    """

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    # ------------------------------------------------------------------
    # Connection helper
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path))
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

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
        sort_column = _VALID_SORT_COLUMNS.get(sort_by, "m.title")
        direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        where_clauses: list[str] = []
        params: list[Any] = []

        if search:
            where_clauses.append("m.title LIKE ?")
            params.append(f"%{search}%")

        if genre:
            # genres is stored as a JSON array of strings, e.g. '["Action","Drama"]'
            where_clauses.append("t.genres LIKE ?")
            params.append(f'%"{genre}"%')

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        connection = self._connect()
        try:
            # Total count for pagination metadata
            count_row = connection.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM movies m
                LEFT JOIN tmdb_movies t ON m.tmdb_movie_id = t.id
                {where_sql}
                """,
                params,
            ).fetchone()
            total: int = count_row["total"]

            # Paginated rows
            offset = (page - 1) * page_size
            rows = connection.execute(
                f"""
                SELECT m.id,
                       m.title,
                       t.poster_path,
                       t.release_date,
                       t.vote_average,
                       t.runtime,
                       t.genres
                FROM movies m
                LEFT JOIN tmdb_movies t ON m.tmdb_movie_id = t.id
                {where_sql}
                ORDER BY {sort_column} {direction}
                LIMIT ? OFFSET ?
                """,
                [*params, page_size, offset],
            ).fetchall()

            items: list[dict[str, Any]] = []
            for row in rows:
                poster_path = row["poster_path"]
                poster_url = (
                    f"{TMDB_IMAGE_BASE}/w500{poster_path}" if poster_path else None
                )

                genres_raw = row["genres"]
                try:
                    genres = json.loads(genres_raw) if genres_raw else []
                except (json.JSONDecodeError, TypeError):
                    genres = []

                items.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "poster_url": poster_url,
                        "release_date": row["release_date"],
                        "vote_average": row["vote_average"],
                        "genres": genres,
                        "runtime": row["runtime"],
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
        finally:
            connection.close()

    # ------------------------------------------------------------------
    # Single movie detail
    # ------------------------------------------------------------------

    def get_movie(self, movie_id: int) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT m.id,
                       m.title,
                       m.tmdb_movie_id,
                       t.id          AS tmdb_pk,
                       t.tmdb_id,
                       t.title       AS tmdb_title,
                       t.original_title,
                       t.overview,
                       t.poster_path,
                       t.backdrop_path,
                       t.release_date,
                       t.vote_average,
                       t.runtime,
                       t.genres,
                       t.imdb_id
                FROM movies m
                LEFT JOIN tmdb_movies t ON m.tmdb_movie_id = t.id
                WHERE m.id = ?
                """,
                (movie_id,),
            ).fetchone()

            if row is None:
                return None

            # Build optional TMDB sub-object
            tmdb: dict[str, Any] | None = None
            if row["tmdb_pk"] is not None:
                tmdb = {
                    "id": row["tmdb_pk"],
                    "tmdb_id": row["tmdb_id"],
                    "title": row["tmdb_title"],
                    "original_title": row["original_title"],
                    "overview": row["overview"],
                    "poster_path": row["poster_path"],
                    "backdrop_path": row["backdrop_path"],
                    "release_date": row["release_date"],
                    "vote_average": row["vote_average"],
                    "runtime": row["runtime"],
                    "genres": row["genres"],
                    "imdb_id": row["imdb_id"],
                }

            # Telegram messages linked to this movie
            messages = connection.execute(
                """
                SELECT id, movie_id, message_id
                FROM telegram_messages
                WHERE movie_id = ?
                ORDER BY message_id
                """,
                (movie_id,),
            ).fetchall()

            telegram_messages = [
                {
                    "id": msg["id"],
                    "movie_id": msg["movie_id"],
                    "message_id": msg["message_id"],
                }
                for msg in messages
            ]

            # Build a deep link to the first Telegram message
            telegram_link = None
            channel_id = get_telegram_channel_id()
            if telegram_messages and channel_id:
                first_msg_id = telegram_messages[0]["message_id"]
                telegram_link = f"https://t.me/c/{channel_id}/{first_msg_id}"

            return {
                "id": row["id"],
                "title": row["title"],
                "tmdb_movie_id": row["tmdb_movie_id"],
                "tmdb": tmdb,
                "telegram_messages": telegram_messages,
                "telegram_link": telegram_link,
            }
        finally:
            connection.close()

    # ------------------------------------------------------------------
    # Distinct genre list
    # ------------------------------------------------------------------

    def get_genres(self) -> list[str]:
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT DISTINCT genres
                FROM tmdb_movies
                WHERE genres IS NOT NULL AND genres != '[]'
                """
            ).fetchall()

            all_genres: set[str] = set()
            for row in rows:
                try:
                    parsed = json.loads(row["genres"])
                    if isinstance(parsed, list):
                        all_genres.update(parsed)
                except (json.JSONDecodeError, TypeError):
                    continue

            return sorted(all_genres)
        finally:
            connection.close()

    # ------------------------------------------------------------------
    # Library statistics
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        connection = self._connect()
        try:
            movie_stats = connection.execute(
                """
                SELECT COUNT(*) AS total_movies,
                       SUM(CASE WHEN tmdb_movie_id IS NOT NULL
                                THEN 1 ELSE 0 END) AS movies_with_tmdb,
                       SUM(CASE WHEN tmdb_movie_id IS NULL
                                THEN 1 ELSE 0 END) AS movies_without_tmdb
                FROM movies
                """
            ).fetchone()

            message_count = connection.execute(
                "SELECT COUNT(*) AS total FROM telegram_messages"
            ).fetchone()

            # Genre breakdown — count how many movies belong to each genre
            genre_rows = connection.execute(
                """
                SELECT genres
                FROM tmdb_movies
                WHERE genres IS NOT NULL AND genres != '[]'
                """
            ).fetchall()

            genre_counts: dict[str, int] = {}
            for row in genre_rows:
                try:
                    parsed = json.loads(row["genres"])
                    if isinstance(parsed, list):
                        for genre in parsed:
                            genre_counts[genre] = genre_counts.get(genre, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue

            return {
                "total_movies": movie_stats["total_movies"],
                "movies_with_tmdb": movie_stats["movies_with_tmdb"],
                "movies_without_tmdb": movie_stats["movies_without_tmdb"],
                "total_messages": message_count["total"],
                "genres_breakdown": dict(
                    sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
                ),
            }
        finally:
            connection.close()
