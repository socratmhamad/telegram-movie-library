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
        print("Migration requires a target PostgreSQL database URL.")
        sys.exit(1)
        
    if pg_url.startswith("postgres://"):
        pg_url = pg_url.replace("postgres://", "postgresql://", 1)

    sqlite_path = os.getenv("DATABASE_PATH", str(Path("database") / "movies.db"))
    if not Path(sqlite_path).exists():
        print(f"ERROR: Source SQLite database not found at {sqlite_path}")
        sys.exit(1)

    print(f"Source SQLite: {sqlite_path}")
    print(f"Target PostgreSQL: {pg_url}")
    
    # 1. Setup Postgres (Target)
    print("\nInitializing PostgreSQL schema...")
    pg_engine = create_engine(pg_url)
    Base.metadata.create_all(pg_engine)
    Session = sessionmaker(bind=pg_engine)
    pg_session = Session()

    # 2. Setup SQLite (Source)
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Disable foreign key checks temporarily in Postgres for bulk inserts
    try:
        # PostgreSQL doesn't have a simple session-level disable for FK checks, 
        # but we can rely on inserting tables in the right order (TMDBMovie -> Movie -> TelegramMessage)
        
        # 3. Migrate tmdb_movies
        print("Migrating tmdb_movies...")
        sqlite_cursor.execute("SELECT * FROM tmdb_movies")
        tmdb_rows = sqlite_cursor.fetchall()
        for r in tmdb_rows:
            # Check if exists to be idempotent
            if pg_session.get(TMDBMovie, r["id"]):
                continue
            pg_session.add(TMDBMovie(
                id=r["id"],
                tmdb_id=r["tmdb_id"],
                title=r["title"],
                original_title=r["original_title"],
                overview=r["overview"],
                poster_path=r["poster_path"],
                backdrop_path=r["backdrop_path"],
                release_date=r["release_date"],
                vote_average=r["vote_average"],
                runtime=r["runtime"],
                genres=r["genres"],
                imdb_id=r["imdb_id"]
            ))
        pg_session.commit()
        print(f"  -> Migrated {len(tmdb_rows)} TMDB movies.")

        # 4. Migrate movies
        print("Migrating movies...")
        sqlite_cursor.execute("SELECT * FROM movies")
        movies_rows = sqlite_cursor.fetchall()
        for r in movies_rows:
            if pg_session.get(Movie, r["id"]):
                continue
            pg_session.add(Movie(
                id=r["id"],
                title=r["title"],
                tmdb_movie_id=r["tmdb_movie_id"]
            ))
        pg_session.commit()
        print(f"  -> Migrated {len(movies_rows)} movies.")

        # 5. Migrate telegram_messages
        print("Migrating telegram_messages...")
        sqlite_cursor.execute("SELECT * FROM telegram_messages")
        msg_rows = sqlite_cursor.fetchall()
        for r in msg_rows:
            if pg_session.get(TelegramMessage, r["id"]):
                continue
            pg_session.add(TelegramMessage(
                id=r["id"],
                movie_id=r["movie_id"],
                message_id=r["message_id"]
            ))
        pg_session.commit()
        print(f"  -> Migrated {len(msg_rows)} Telegram messages.")

        # 6. Reset Sequences (CRITICAL for PostgreSQL autoincrement)
        # SQLite just uses MAX(id)+1, but PostgreSQL uses a Sequence object linked to the SERIAL column.
        # When we manually insert IDs, the sequence isn't advanced. We must update it.
        if pg_engine.dialect.name == "postgresql":
            print("\nUpdating PostgreSQL sequences...")
            for table_name in ["tmdb_movies", "movies", "telegram_messages"]:
                pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 1)) FROM {table_name};"))
            pg_session.commit()
            print("  -> Sequences updated.")
            
        print("\nMigration completed successfully!")

    except Exception as e:
        pg_session.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        pg_session.close()
        sqlite_conn.close()

if __name__ == "__main__":
    main()
