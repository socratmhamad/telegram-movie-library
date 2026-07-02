import os
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.models import Base, TMDBMovie, Movie, TelegramMessage

# Load env variables
load_dotenv(Path(__file__).resolve().parent / ".env")


def main():
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
    print(f"Target PostgreSQL: {pg_url}")

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
        print("✓ TMDB movies imported")

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
                    "title": r["title"],
                    "tmdb_movie_id": r["tmdb_movie_id"],
                }
                for r in movies_rows
            ],
        )

        session.commit()
        print("✓ Movies imported")

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
        print("✓ Telegram messages imported")

        # ------------------------------------------------------------------
        # RESET SEQUENCES
        # ------------------------------------------------------------------

        if pg_engine.dialect.name == "postgresql":
            print("\nUpdating PostgreSQL sequences...")

            for table in [
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

        print("\n===================================")
        print("Migration completed successfully!")
        print("===================================")

    except Exception as e:
        session.rollback()
        raise

    finally:
        session.close()
        sqlite_conn.close()


if __name__ == "__main__":
    main()