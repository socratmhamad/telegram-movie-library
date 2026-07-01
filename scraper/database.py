from __future__ import annotations

from contextlib import contextmanager
import json
import sqlite3
from pathlib import Path
from typing import Iterator, Iterable


class MovieDatabase:
    """Small SQLite repository for storing scraped Telegram movie records."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            if self._schema_is_current(connection):
                self._create_indexes(connection)
                return

            self._migrate_schema(connection)

    def _schema_is_current(self, connection: sqlite3.Connection) -> bool:
        movies_columns = self._table_columns(connection, "movies")
        messages_columns = self._table_columns(connection, "telegram_messages")
        tmdb_columns = self._table_columns(connection, "tmdb_movies")
        return (
            movies_columns == ["id", "title", "tmdb_movie_id"]
            and messages_columns == ["id", "movie_id", "message_id"]
            and tmdb_columns == [
                "id",
                "tmdb_id",
                "title",
                "original_title",
                "overview",
                "poster_path",
                "backdrop_path",
                "release_date",
                "vote_average",
                "runtime",
                "genres",
                "imdb_id",
            ]
        )

    def _table_exists(self, connection: sqlite3.Connection, table_name: str) -> bool:
        return bool(
            connection.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """,
                (table_name,),
            ).fetchone()
        )

    def _table_columns(self, connection: sqlite3.Connection, table_name: str) -> list[str]:
        if not self._table_exists(connection, table_name):
            return []

        return [
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]

    def _migrate_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute("PRAGMA foreign_keys = OFF")
        has_legacy_movies = self._table_exists(connection, "movies")
        has_legacy_messages = self._table_exists(connection, "telegram_messages")
        has_legacy_tmdb = self._table_exists(connection, "tmdb_movies")

        if has_legacy_messages:
            connection.execute("ALTER TABLE telegram_messages RENAME TO telegram_messages_legacy")
        if has_legacy_movies:
            connection.execute("ALTER TABLE movies RENAME TO movies_legacy")
        if has_legacy_tmdb:
            connection.execute("ALTER TABLE tmdb_movies RENAME TO tmdb_movies_legacy")

        self._create_schema(connection)

        if has_legacy_tmdb:
            self._migrate_legacy_tmdb_movies(connection)

        if not has_legacy_movies:
            self._drop_legacy_tables(connection)
            connection.execute("PRAGMA foreign_keys = ON")
            return

        legacy_columns = set(self._table_columns(connection, "movies_legacy"))
        if {"id", "title"}.issubset(legacy_columns) and has_legacy_messages:
            if "tmdb_movie_id" in legacy_columns:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO movies (id, title, tmdb_movie_id)
                    SELECT id, title, tmdb_movie_id
                    FROM movies_legacy
                    WHERE title IS NOT NULL
                    """
                )
            else:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO movies (id, title, tmdb_movie_id)
                    SELECT id, title, NULL
                    FROM movies_legacy
                    WHERE title IS NOT NULL
                    """
                )
            connection.execute(
                """
                INSERT OR IGNORE INTO telegram_messages (id, movie_id, message_id)
                SELECT id, movie_id, message_id
                FROM telegram_messages_legacy
                WHERE movie_id IS NOT NULL AND message_id IS NOT NULL
                """
            )
        elif {"title", "message_id"}.issubset(legacy_columns):
            connection.execute(
                """
                INSERT OR IGNORE INTO movies (title)
                SELECT DISTINCT title
                FROM movies_legacy
                WHERE title IS NOT NULL AND message_id IS NOT NULL
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO telegram_messages (movie_id, message_id)
                SELECT movies.id, movies_legacy.message_id
                FROM movies_legacy
                JOIN movies ON movies.title = movies_legacy.title
                WHERE movies_legacy.message_id IS NOT NULL
                """
            )

        self._drop_legacy_tables(connection)
        connection.execute("PRAGMA foreign_keys = ON")

    def _migrate_legacy_tmdb_movies(self, connection: sqlite3.Connection) -> None:
        legacy_columns = set(self._table_columns(connection, "tmdb_movies_legacy"))
        required_columns = {
            "tmdb_id",
            "title",
            "original_title",
            "overview",
            "poster_path",
            "backdrop_path",
            "release_date",
            "vote_average",
            "runtime",
            "genres",
            "imdb_id",
        }
        if not required_columns.issubset(legacy_columns):
            return

        connection.execute(
            """
            INSERT OR IGNORE INTO tmdb_movies (
                id,
                tmdb_id,
                title,
                original_title,
                overview,
                poster_path,
                backdrop_path,
                release_date,
                vote_average,
                runtime,
                genres,
                imdb_id
            )
            SELECT
                id,
                tmdb_id,
                title,
                original_title,
                overview,
                poster_path,
                backdrop_path,
                release_date,
                vote_average,
                runtime,
                genres,
                imdb_id
            FROM tmdb_movies_legacy
            """
        )

    def _drop_legacy_tables(self, connection: sqlite3.Connection) -> None:
        connection.execute("DROP TABLE IF EXISTS telegram_messages_legacy")
        connection.execute("DROP TABLE IF EXISTS movies_legacy")
        connection.execute("DROP TABLE IF EXISTS tmdb_movies_legacy")

    def _create_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tmdb_movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tmdb_id INTEGER NOT NULL UNIQUE,
                title TEXT,
                original_title TEXT,
                overview TEXT,
                poster_path TEXT,
                backdrop_path TEXT,
                release_date TEXT,
                vote_average REAL,
                runtime INTEGER,
                genres TEXT,
                imdb_id TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                tmdb_movie_id INTEGER,
                FOREIGN KEY (tmdb_movie_id) REFERENCES tmdb_movies (id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS telegram_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
            )
            """
        )
        self._create_indexes(connection)

    def _create_indexes(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_movies_title
            ON movies (title)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_telegram_messages_movie_id
            ON telegram_messages (movie_id)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_movies_tmdb_movie_id
            ON movies (tmdb_movie_id)
            """
        )

    def get_known_message_ids(self) -> set[int]:
        """Return the set of all Telegram message IDs already stored."""
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT message_id FROM telegram_messages"
            ).fetchall()
            return {int(row["message_id"]) for row in rows}

    def get_or_create_movie(self, title: str) -> int:
        with self._connection() as connection:
            return self._get_or_create_movie(connection, title)

    def save_telegram_message(self, movie_id: int, message_id: int) -> bool:
        with self._connection() as connection:
            return self._save_telegram_message(connection, movie_id, message_id)

    def save_movie_message(self, title: str, message_id: int) -> bool:
        with self._connection() as connection:
            movie_id = self._get_or_create_movie(connection, title)
            return self._save_telegram_message(connection, movie_id, message_id)

    def save_movies(self, movies: Iterable[dict[str, object]]) -> int:
        saved_count = 0
        with self._connection() as connection:
            for movie in movies:
                movie_id = self._get_or_create_movie(connection, str(movie["title"]))
                inserted = self._save_telegram_message(
                    connection,
                    movie_id,
                    int(movie["message_id"]),
                )
                if inserted:
                    saved_count += 1

        return saved_count

    def get_movies_without_tmdb(self) -> list[sqlite3.Row]:
        with self._connection() as connection:
            return connection.execute(
                """
                SELECT id, title
                FROM movies
                WHERE tmdb_movie_id IS NULL
                ORDER BY title
                """
            ).fetchall()

    def save_tmdb_movie(self, tmdb_movie: dict[str, object]) -> int:
        with self._connection() as connection:
            return self._save_tmdb_movie(connection, tmdb_movie)

    def link_movie_to_tmdb(self, movie_id: int, tmdb_movie_id: int) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                UPDATE movies
                SET tmdb_movie_id = ?
                WHERE id = ?
                """,
                (tmdb_movie_id, movie_id),
            )

    def _get_or_create_movie(self, connection: sqlite3.Connection, title: str) -> int:
        connection.execute(
            """
            INSERT OR IGNORE INTO movies (title)
            VALUES (?)
            """,
            (title,),
        )
        row = connection.execute(
            """
            SELECT id
            FROM movies
            WHERE title = ?
            """,
            (title,),
        ).fetchone()

        if row is None:
            raise RuntimeError(f"Unable to create or find movie title: {title}")

        return int(row["id"])

    def _save_telegram_message(
        self,
        connection: sqlite3.Connection,
        movie_id: int,
        message_id: int,
    ) -> bool:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO telegram_messages (movie_id, message_id)
            VALUES (?, ?)
            """,
            (movie_id, message_id),
        )
        return cursor.rowcount > 0

    def _save_tmdb_movie(
        self,
        connection: sqlite3.Connection,
        tmdb_movie: dict[str, object],
    ) -> int:
        genres = tmdb_movie.get("genres")
        genres_value = json.dumps(genres if isinstance(genres, list) else [])
        connection.execute(
            """
            INSERT OR IGNORE INTO tmdb_movies (
                tmdb_id,
                title,
                original_title,
                overview,
                poster_path,
                backdrop_path,
                release_date,
                vote_average,
                runtime,
                genres,
                imdb_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tmdb_movie["tmdb_id"],
                tmdb_movie.get("title"),
                tmdb_movie.get("original_title"),
                tmdb_movie.get("overview"),
                tmdb_movie.get("poster_path"),
                tmdb_movie.get("backdrop_path"),
                tmdb_movie.get("release_date"),
                tmdb_movie.get("vote_average"),
                tmdb_movie.get("runtime"),
                genres_value,
                tmdb_movie.get("imdb_id"),
            ),
        )
        row = connection.execute(
            """
            SELECT id
            FROM tmdb_movies
            WHERE tmdb_id = ?
            """,
            (tmdb_movie["tmdb_id"],),
        ).fetchone()

        if row is None:
            raise RuntimeError(f"Unable to create or find TMDB movie: {tmdb_movie['tmdb_id']}")

        return int(row["id"])
