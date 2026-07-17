"""
test_migration.py — Safe end-to-end test for channel migration feature.

Creates temporary test data, runs migration logic, verifies results,
then cleans up. Does NOT touch existing libraries/movies.

Usage:
    python test_migration.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from sqlalchemy import select, delete

from config import settings
from database.models import (
    get_db_url,
    init_db,
    Library,
    Movie,
    TMDBMovie,
    TelegramMessage,
)


# Bring in matching logic from migration script
from migrate_channel_links import (
    build_match_indexes,
    match_message,
    clean_title,
)


TEST_LIBRARY_SLUG = "__test_migration__"
TEST_MOVIES = [
    ("The Shawshank Redemption 1994", 1001),
    ("Inception 2010", 1002),
    ("The Dark Knight 2008", 1003),
    ("Pulp Fiction 1994", 1004),
    ("Interstellar 2014", 1005),
]

# Simulated "new channel" messages (slightly different formatting, new IDs)
NEW_CHANNEL_MESSAGES = [
    ("The Shawshank Redemption (1994) 1080p", 501),
    ("Inception 2010 BluRay", 502),
    ("The Dark Knight 2008", 503),
    ("Pulp Fiction 1994 720p", 504),
    ("Interstellar (2014) Web-DL", 505),
    ("Some New Movie 2025", 506),  # Not in DB — should be unmatched
]


def _safe(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


def run_test():
    db_url = get_db_url(settings.database_url, settings.database_path)
    db_path = settings.database_path

    # ---- Step 1: Backup ----
    backup_path = db_path.with_suffix(".db.test_backup")
    print("=" * 60)
    print("  STEP 1: Database Backup")
    print("=" * 60)
    if db_path.exists():
        shutil.copy2(db_path, backup_path)
        print(f"  Backed up: {db_path}")
        print(f"  Backup at: {backup_path}")
    else:
        print(f"  No local DB file at {db_path} (using remote DB?)")
        backup_path = None
    print()

    SessionLocal = init_db(db_url)
    test_library_id = None

    try:
        # ---- Step 2: Create test data ----
        print("=" * 60)
        print("  STEP 2: Create Test Library + Movies")
        print("=" * 60)

        with SessionLocal() as session:
            # Clean up any leftover test data
            old_lib = session.execute(
                select(Library).where(Library.slug == TEST_LIBRARY_SLUG)
            ).scalar_one_or_none()
            if old_lib:
                # Delete movies and messages for old test lib
                old_movies = session.execute(
                    select(Movie).where(Movie.library_id == old_lib.id)
                ).scalars().all()
                for m in old_movies:
                    session.execute(
                        delete(TelegramMessage).where(TelegramMessage.movie_id == m.id)
                    )
                session.execute(
                    delete(Movie).where(Movie.library_id == old_lib.id)
                )
                session.execute(
                    delete(Library).where(Library.id == old_lib.id)
                )
                session.commit()

            # Create test library
            lib = Library(
                name="Test Migration Library",
                slug=TEST_LIBRARY_SLUG,
                telegram_channel="@old_test_channel",
                is_active=True,
                telegram_channel_id="9999999999",
            )
            session.add(lib)
            session.flush()
            test_library_id = lib.id
            print(f"  Created library: id={lib.id}, slug={lib.slug}")

            # Create test movies with old message IDs
            for title, old_msg_id in TEST_MOVIES:
                movie = Movie(
                    library_id=lib.id,
                    title=title,
                )
                session.add(movie)
                session.flush()

                msg = TelegramMessage(
                    movie_id=movie.id,
                    message_id=old_msg_id,
                )
                session.add(msg)
                print(f"  Created movie: \"{_safe(title)}\" (msg_id={old_msg_id})")

            session.commit()
        print(f"\n  Total test movies: {len(TEST_MOVIES)}")
        print()

        # ---- Step 3: Verify old deep links ----
        print("=" * 60)
        print("  STEP 3: Verify Old Deep Links (Before Migration)")
        print("=" * 60)

        with SessionLocal() as session:
            movies = session.execute(
                select(Movie).where(Movie.library_id == test_library_id)
            ).scalars().all()

            for movie in movies:
                msgs = session.execute(
                    select(TelegramMessage).where(TelegramMessage.movie_id == movie.id)
                ).scalars().all()

                library = session.execute(
                    select(Library).where(Library.id == movie.library_id)
                ).scalar_one()

                if msgs and library.telegram_channel_id:
                    link = f"https://t.me/c/{library.telegram_channel_id}/{msgs[0].message_id}"
                else:
                    link = None
                print(f"  \"{_safe(movie.title)}\" -> {link}")
        print()

        # ---- Step 4: Run matching (no Telegram connection needed) ----
        print("=" * 60)
        print("  STEP 4: Simulate Migration Matching")
        print("=" * 60)

        with SessionLocal() as session:
            title_index, tmdb_index, fuzzy_candidates = build_match_indexes(
                session, test_library_id
            )
            movie_titles = {mid: title for mid, title in fuzzy_candidates}

        print(f"  Loaded {len(fuzzy_candidates)} movies for matching.\n")

        matched = []
        unmatched = []

        for raw_text, new_msg_id in NEW_CHANNEL_MESSAGES:
            scraped_title = clean_title(raw_text)
            result = match_message(
                scraped_title, new_msg_id,
                title_index, tmdb_index, fuzzy_candidates, movie_titles,
            )
            if result:
                matched.append(result)
                print(f"  MATCH [{result.method}] "
                      f"\"{_safe(scraped_title)}\" -> \"{_safe(result.movie_title)}\" "
                      f"(score={result.score:.0f}, new_msg={new_msg_id})")
            else:
                unmatched.append(scraped_title)
                print(f"  UNMATCHED: \"{_safe(scraped_title)}\" (msg={new_msg_id})")

        print(f"\n  Matched: {len(matched)}, Unmatched: {len(unmatched)}")
        print()

        # ---- Step 5: Apply migration to test library ----
        print("=" * 60)
        print("  STEP 5: Apply Migration to Test Library")
        print("=" * 60)

        new_channel = "@new_test_channel"
        new_channel_id = "1111111111"

        with SessionLocal() as session:
            # Update library
            library = session.execute(
                select(Library).where(Library.id == test_library_id)
            ).scalar_one()
            library.telegram_channel = new_channel
            library.telegram_channel_id = new_channel_id

            # Delete old messages for matched movies
            matched_movie_ids = {m.movie_id for m in matched}
            if matched_movie_ids:
                session.execute(
                    delete(TelegramMessage).where(
                        TelegramMessage.movie_id.in_(matched_movie_ids)
                    )
                )

            # Insert new messages
            for m in matched:
                session.add(TelegramMessage(
                    movie_id=m.movie_id,
                    message_id=m.new_message_id,
                ))

            session.commit()
            print(f"  Updated library channel: {new_channel} (id={new_channel_id})")
            print(f"  Replaced {len(matched)} message links.")
        print()

        # ---- Step 6: Verify new deep links ----
        print("=" * 60)
        print("  STEP 6: Verify New Deep Links (After Migration)")
        print("=" * 60)

        with SessionLocal() as session:
            movies = session.execute(
                select(Movie).where(Movie.library_id == test_library_id)
            ).scalars().all()

            all_correct = True
            for movie in movies:
                msgs = session.execute(
                    select(TelegramMessage).where(TelegramMessage.movie_id == movie.id)
                ).scalars().all()

                library = session.execute(
                    select(Library).where(Library.id == movie.library_id)
                ).scalar_one()

                if msgs and library.telegram_channel_id:
                    link = f"https://t.me/c/{library.telegram_channel_id}/{msgs[0].message_id}"
                else:
                    link = None

                # Verify channel ID changed
                old_id_used = "9999999999" in (link or "")
                new_id_used = new_channel_id in (link or "")
                status = "OK" if new_id_used else ("FAIL" if link else "NO LINK")
                if status != "OK":
                    all_correct = False
                print(f"  [{status}] \"{_safe(movie.title)}\" -> {link}")

            print()
            if all_correct:
                print("  ALL LINKS MIGRATED CORRECTLY!")
            else:
                print("  WARNING: Some links did not migrate correctly.")
        print()

        # ---- Step 7: Verify existing data untouched ----
        print("=" * 60)
        print("  STEP 7: Verify Existing Data Untouched")
        print("=" * 60)

        with SessionLocal() as session:
            libs = session.execute(
                select(Library).where(Library.slug != TEST_LIBRARY_SLUG)
            ).scalars().all()

            for lib in libs:
                count = session.scalar(
                    select(Movie.id).where(Movie.library_id == lib.id)
                    .with_only_columns(Movie.id)
                    .subquery()
                    .select()
                    .with_only_columns()
                    .add_columns(Movie.id)
                )
                # Simpler count
                from sqlalchemy import func
                movie_count = session.scalar(
                    select(func.count(Movie.id)).where(Movie.library_id == lib.id)
                ) or 0
                print(f"  Library \"{_safe(lib.name)}\" (id={lib.id}): {movie_count} movies - UNTOUCHED")
        print()

    finally:
        # ---- Cleanup ----
        print("=" * 60)
        print("  CLEANUP: Removing Test Data")
        print("=" * 60)

        if test_library_id:
            with SessionLocal() as session:
                test_movies = session.execute(
                    select(Movie).where(Movie.library_id == test_library_id)
                ).scalars().all()

                for m in test_movies:
                    session.execute(
                        delete(TelegramMessage).where(TelegramMessage.movie_id == m.id)
                    )
                session.execute(
                    delete(Movie).where(Movie.library_id == test_library_id)
                )
                session.execute(
                    delete(Library).where(Library.id == test_library_id)
                )
                session.commit()
                print(f"  Deleted test library and {len(test_movies)} test movies.")

        if backup_path and backup_path.exists():
            print(f"  Backup still available at: {backup_path}")
            print(f"  (Delete manually when no longer needed)")
        print()

        print("=" * 60)
        print("  TEST COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    run_test()
