"""Migrate local SQLite data to Supabase PostgreSQL.

Reads DATABASE_URL directly from .env (bypasses APP_ENV gate) since this
script is explicitly for pushing data to production.

Usage:
    python migrate_to_postgres.py
"""

import os
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.models import Base, Library, TMDBMovie, Movie, TelegramMessage

# Load env variables
load_dotenv(Path(__file__).resolve().parent / ".env")


def main():
    # Fix Windows console encoding
    import io
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    force = "--force" in sys.argv

    pg_url = os.getenv("DATABASE_URL")
    if not pg_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        sys.exit(1)

    if pg_url.startswith("postgres://"):
        pg_url = pg_url.replace("postgres://", "postgresql://", 1)

    sqlite_path = os.getenv("DATABASE_PATH", "database/movies.db")

    if not Path(sqlite_path).exists():
        print(f"ERROR: SQLite database not found: {sqlite_path}")
        sys.exit(1)

    print(f"Source SQLite: {sqlite_path}")
    print(f"Target PostgreSQL: {pg_url.split('@')[-1] if '@' in pg_url else pg_url}")

    print("\nInitializing PostgreSQL schema...")

    pg_engine = create_engine(pg_url)
    Base.metadata.create_all(pg_engine)

    Session = sessionmaker(bind=pg_engine)
    session = Session()

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()

    try:

        # ------------------------------------------------------------------
        # Safety check: warn if target tables already have data
        # ------------------------------------------------------------------
        existing_movies = session.scalar(text("SELECT COUNT(*) FROM movies")) or 0
        existing_libs = session.scalar(text("SELECT COUNT(*) FROM libraries")) or 0
        if existing_movies > 0 or existing_libs > 0:
            print(f"\nWARNING: Target database already has {existing_libs} libraries, {existing_movies} movies.")
            if not force:
                answer = input("Clear and re-import? (y/N): ").strip().lower()
                if answer != "y":
                    print("Aborted. Use --force to skip this prompt.")
                    return

            # Clear existing data in reverse FK order
            print("Clearing existing data...")
            session.execute(text("DELETE FROM telegram_messages"))
            session.execute(text("DELETE FROM movies"))
            session.execute(text("DELETE FROM tmdb_movies"))
            session.execute(text("DELETE FROM libraries"))
            session.commit()
            print("[OK] Existing data cleared")

        # ------------------------------------------------------------------
        # Fix stale constraint: drop UNIQUE(message_id) if it exists
        # The correct constraint is UNIQUE(movie_id, message_id)
        # ------------------------------------------------------------------
        if pg_engine.dialect.name == "postgresql":
            stale_constraints = session.execute(text("""
                SELECT constraint_name FROM information_schema.table_constraints
                WHERE table_name = 'telegram_messages'
                  AND constraint_type = 'UNIQUE'
                  AND constraint_name = 'telegram_messages_message_id_key'
            """)).fetchall()
            if stale_constraints:
                print("\nDropping stale UNIQUE(message_id) constraint...")
                session.execute(text(
                    "ALTER TABLE telegram_messages DROP CONSTRAINT telegram_messages_message_id_key"
                ))
                session.commit()
                print("[OK] Stale constraint dropped")

        # ------------------------------------------------------------------
        # LIBRARIES
        # ------------------------------------------------------------------

        print("\nReading libraries...")
        cursor.execute("SELECT * FROM libraries")
        lib_rows = cursor.fetchall()

        print(f"Importing {len(lib_rows)} libraries...")

        session.bulk_insert_mappings(
            Library,
            [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "slug": r["slug"],
                    "telegram_channel": r["telegram_channel"],
                    "is_active": bool(r["is_active"]) if r["is_active"] is not None else None,
                    "last_scan": r["last_scan"],
                    "last_migration": r["last_migration"],
                    "telegram_channel_id": r["telegram_channel_id"],
                }
                for r in lib_rows
            ],
        )

        session.commit()
        print("[OK] Libraries imported")

        # ------------------------------------------------------------------
        # TMDB MOVIES
        # ------------------------------------------------------------------

        print("\nReading tmdb_movies...")
        cursor.execute("SELECT * FROM tmdb_movies")
        tmdb_rows = cursor.fetchall()

        print(f"Importing {len(tmdb_rows)} TMDB movies...")

        session.bulk_insert_mappings(
            TMDBMovie,
            [
                {
                    "id": r["id"],
                    "tmdb_id": r["tmdb_id"],
                    "title": r["title"],
                    "original_title": r["original_title"],
                    "overview": r["overview"],
                    "poster_path": r["poster_path"],
                    "backdrop_path": r["backdrop_path"],
                    "release_date": r["release_date"],
                    "vote_average": r["vote_average"],
                    "runtime": r["runtime"],
                    "genres": r["genres"],
                    "imdb_id": r["imdb_id"],
                }
                for r in tmdb_rows
            ],
        )

        session.commit()
        print("[OK] TMDB movies imported")

        # ------------------------------------------------------------------
        # MOVIES
        # ------------------------------------------------------------------

        print("\nReading movies...")
        cursor.execute("SELECT * FROM movies")
        movies_rows = cursor.fetchall()

        print(f"Importing {len(movies_rows)} movies...")

        session.bulk_insert_mappings(
            Movie,
            [
                {
                    "id": r["id"],
                    "library_id": r["library_id"],
                    "title": r["title"],
                    "tmdb_movie_id": r["tmdb_movie_id"],
                }
                for r in movies_rows
            ],
        )

        session.commit()
        print("[OK] Movies imported")

        # ------------------------------------------------------------------
        # TELEGRAM MESSAGES
        # ------------------------------------------------------------------

        print("\nReading telegram_messages...")
        cursor.execute("SELECT * FROM telegram_messages")
        msg_rows = cursor.fetchall()

        print(f"Importing {len(msg_rows)} telegram messages...")

        session.bulk_insert_mappings(
            TelegramMessage,
            [
                {
                    "id": r["id"],
                    "movie_id": r["movie_id"],
                    "message_id": r["message_id"],
                }
                for r in msg_rows
            ],
        )

        session.commit()
        print("[OK] Telegram messages imported")

        # ------------------------------------------------------------------
        # RESET SEQUENCES
        # ------------------------------------------------------------------

        if pg_engine.dialect.name == "postgresql":
            print("\nUpdating PostgreSQL sequences...")

            for table in [
                "libraries",
                "tmdb_movies",
                "movies",
                "telegram_messages",
            ]:
                session.execute(
                    text(
                        f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE((SELECT MAX(id) FROM {table}), 1),
                            true
                        );
                        """
                    )
                )

            session.commit()

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------

        lib_count = session.scalar(text("SELECT COUNT(*) FROM libraries"))
        tmdb_count = session.scalar(text("SELECT COUNT(*) FROM tmdb_movies"))
        movie_count = session.scalar(text("SELECT COUNT(*) FROM movies"))
        msg_count = session.scalar(text("SELECT COUNT(*) FROM telegram_messages"))

        print("\n===================================")
        print("  Migration completed successfully!")
        print("===================================")
        print(f"  Libraries          : {lib_count}")
        print(f"  TMDB movies        : {tmdb_count}")
        print(f"  Movies             : {movie_count}")
        print(f"  Telegram messages  : {msg_count}")
        print("===================================")

    except Exception as e:
        session.rollback()
        print(f"\nERROR: Migration failed: {e}")
        raise

    finally:
        session.close()
        sqlite_conn.close()


if __name__ == "__main__":
    main()