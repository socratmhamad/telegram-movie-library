"""
fix_message_id_constraint.py — One-time schema migration.

Removes the old UNIQUE constraint on telegram_messages.message_id
and replaces it with a composite UNIQUE(movie_id, message_id).

SQLite doesn't support ALTER TABLE DROP CONSTRAINT, so we rebuild the table.

Usage:
    python fix_message_id_constraint.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from config import settings


def migrate():
    db_path = settings.database_path
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        sys.exit(1)

    print(f"Database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = OFF")

    try:
        # Check current schema
        schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE name='telegram_messages'"
        ).fetchone()

        if schema:
            print(f"\nCurrent schema:\n  {schema[0]}\n")
        else:
            print("Table telegram_messages not found!")
            sys.exit(1)

        # Check if already migrated
        if "uix_message_movie" in (schema[0] or ""):
            print("Already migrated — composite constraint exists.")
            return

        print("Rebuilding table with composite unique constraint...")

        conn.executescript("""
            -- 1. Rename old table
            ALTER TABLE telegram_messages RENAME TO telegram_messages_old;

            -- 2. Create new table with composite constraint
            CREATE TABLE telegram_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
                UNIQUE (movie_id, message_id)
            );

            -- 3. Copy data
            INSERT INTO telegram_messages (id, movie_id, message_id)
            SELECT id, movie_id, message_id FROM telegram_messages_old;

            -- 4. Drop old table
            DROP TABLE telegram_messages_old;
        """)

        # Recreate index
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_telegram_messages_movie_id
            ON telegram_messages (movie_id)
        """)

        conn.commit()

        # Verify
        new_schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE name='telegram_messages'"
        ).fetchone()
        print(f"\nNew schema:\n  {new_schema[0]}\n")

        count = conn.execute("SELECT COUNT(*) FROM telegram_messages").fetchone()[0]
        print(f"Rows preserved: {count}")
        print("\nDone. Schema migration complete.")

    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == "__main__":
    migrate()
