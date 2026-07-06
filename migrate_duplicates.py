import sqlite3
import os
from pathlib import Path

DB_PATH = Path("database/movies.db")

def migrate():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return

    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Disable foreign keys for schema migration
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # 1. Add future quality columns to telegram_messages
    print("Updating telegram_messages table...")
    try:
        cursor.execute("ALTER TABLE telegram_messages ADD COLUMN quality VARCHAR;")
        cursor.execute("ALTER TABLE telegram_messages ADD COLUMN codec VARCHAR;")
        cursor.execute("ALTER TABLE telegram_messages ADD COLUMN release_type VARCHAR;")
        cursor.execute("ALTER TABLE telegram_messages ADD COLUMN file_size VARCHAR;")
        cursor.execute("ALTER TABLE telegram_messages ADD COLUMN language VARCHAR;")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columns already exist, skipping.")
        else:
            raise e

    # 2. Create movie_aliases table
    print("Creating movie_aliases table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movie_aliases (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            movie_id INTEGER NOT NULL,
            CONSTRAINT uix_alias_title_library UNIQUE (title, library_id),
            FOREIGN KEY(library_id) REFERENCES libraries (id),
            FOREIGN KEY(movie_id) REFERENCES movies (id) ON DELETE CASCADE
        );
    """)

    # 3. Populate aliases from existing movies
    print("Populating movie aliases...")
    cursor.execute("SELECT id, title, library_id FROM movies")
    movies = cursor.fetchall()
    
    for m in movies:
        try:
            cursor.execute(
                "INSERT INTO movie_aliases (library_id, title, movie_id) VALUES (?, ?, ?)",
                (m['library_id'], m['title'], m['id'])
            )
        except sqlite3.IntegrityError:
            # Already exists
            pass

    # 4. Find duplicates by TMDB ID
    print("Identifying and merging duplicates...")
    # Find all combinations of library_id and tmdb_movie_id that have more than 1 movie
    cursor.execute("""
        SELECT library_id, tmdb_movie_id 
        FROM movies 
        WHERE tmdb_movie_id IS NOT NULL 
        GROUP BY library_id, tmdb_movie_id 
        HAVING COUNT(*) > 1
    """)
    duplicate_groups = cursor.fetchall()

    for group in duplicate_groups:
        library_id = group['library_id']
        tmdb_movie_id = group['tmdb_movie_id']
        
        # Get all movies in this group ordered by id
        cursor.execute("""
            SELECT id FROM movies 
            WHERE library_id = ? AND tmdb_movie_id = ? 
            ORDER BY id ASC
        """, (library_id, tmdb_movie_id))
        
        movies_in_group = [row['id'] for row in cursor.fetchall()]
        
        if len(movies_in_group) > 1:
            primary_id = movies_in_group[0]
            duplicate_ids = movies_in_group[1:]
            
            print(f"Merging duplicates for TMDB ID {tmdb_movie_id} into primary movie {primary_id}...")
            for dup_id in duplicate_ids:
                # Update aliases to point to primary
                cursor.execute("UPDATE movie_aliases SET movie_id = ? WHERE movie_id = ?", (primary_id, dup_id))
                
                # Update telegram_messages to point to primary
                cursor.execute("UPDATE telegram_messages SET movie_id = ? WHERE movie_id = ?", (primary_id, dup_id))
                
                # Delete duplicate movie
                cursor.execute("DELETE FROM movies WHERE id = ?", (dup_id,))

    # 5. Recreate movies table to change constraints
    print("Recreating movies table with new constraints...")
    cursor.execute("""
        CREATE TABLE movies_new (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            tmdb_movie_id INTEGER,
            CONSTRAINT uix_movie_tmdb_library UNIQUE (tmdb_movie_id, library_id),
            FOREIGN KEY(library_id) REFERENCES libraries (id),
            FOREIGN KEY(tmdb_movie_id) REFERENCES tmdb_movies (id)
        );
    """)
    
    # Copy data
    cursor.execute("""
        INSERT INTO movies_new (id, library_id, title, tmdb_movie_id)
        SELECT id, library_id, title, tmdb_movie_id FROM movies;
    """)
    
    # Swap tables
    cursor.execute("DROP TABLE movies;")
    cursor.execute("ALTER TABLE movies_new RENAME TO movies;")

    # Re-enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
