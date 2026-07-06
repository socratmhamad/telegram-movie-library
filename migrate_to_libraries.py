import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv

def migrate():
    # Load .env
    load_dotenv()
    telegram_channel = os.getenv("TELEGRAM_CHANNEL")
    if not telegram_channel:
        print("No TELEGRAM_CHANNEL found in .env, using default '-100123456'")
        telegram_channel = "-100123456"

    db_path = Path("database") / "movies.db"
    if not db_path.exists():
        print(f"Database not found at {db_path}. Assuming fresh installation.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if library_id column exists
    cursor.execute("PRAGMA table_info(movies)")
    columns = [col[1] for col in cursor.fetchall()]
    if "library_id" in columns:
        print("Migration already applied (library_id column exists).")
        return

    print("Starting migration...")
    
    # 1. Create libraries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libraries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL UNIQUE,
            slug VARCHAR NOT NULL UNIQUE,
            telegram_channel VARCHAR NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT 1,
            last_scan DATETIME,
            last_migration DATETIME
        )
    """)
    print("Created libraries table.")

    # 2. Insert default library
    cursor.execute("""
        INSERT OR IGNORE INTO libraries (name, slug, telegram_channel, is_active)
        VALUES (?, ?, ?, ?)
    """, ("General Movies", "general-movies", telegram_channel, 1))
    
    # Get library_id
    cursor.execute("SELECT id FROM libraries WHERE slug = 'general-movies'")
    library_id = cursor.fetchone()[0]
    print(f"Using default library 'General Movies' with ID {library_id}.")

    # 3. Create new movies table
    cursor.execute("""
        CREATE TABLE movies_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            tmdb_movie_id INTEGER,
            FOREIGN KEY(library_id) REFERENCES libraries(id),
            FOREIGN KEY(tmdb_movie_id) REFERENCES tmdb_movies(id),
            CONSTRAINT uix_movie_title_library UNIQUE (title, library_id)
        )
    """)
    print("Created movies_new table.")

    # 4. Copy data
    cursor.execute("""
        INSERT INTO movies_new (id, library_id, title, tmdb_movie_id)
        SELECT id, ?, title, tmdb_movie_id FROM movies
    """, (library_id,))
    print(f"Copied {cursor.rowcount} movies.")

    # 5. Drop old table and rename new
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("DROP TABLE movies")
    cursor.execute("ALTER TABLE movies_new RENAME TO movies")
    cursor.execute("PRAGMA foreign_keys = ON")
    print("Swapped movies table.")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
