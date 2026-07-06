from __future__ import annotations

import json
import os
import time
from pathlib import Path

from sqlalchemy import select

from backend.config import get_database_path, get_database_url
from database.models import TMDBMovie, get_db_url, init_db
from tmdb_service import _tmdb_get

STATE_FILE = Path(__file__).parent / "tmdb_arabic_migration_state.json"

def load_state() -> set[int]:
    """Load the set of already processed TMDB IDs."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_state(processed: set[int]) -> None:
    """Save the set of processed TMDB IDs atomically."""
    temp_file = STATE_FILE.with_suffix(".json.tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(list(processed), f)
    temp_file.replace(STATE_FILE)

def fetch_arabic_metadata(tmdb_id: int) -> dict | None:
    """
    Fetch TMDB metadata preferring Arabic.
    Falls back to English if the Arabic title or overview is missing.
    Returns None if the movie is completely missing from TMDB (e.g. 404).
    """
    try:
        ar_response = _tmdb_get(f"/movie/{tmdb_id}", {"language": "ar"})
    except Exception as e:
        print(f"    - API Error on Arabic fetch: {e}")
        return None

    ar_title = (ar_response.get("title") or "").strip()
    ar_overview = (ar_response.get("overview") or "").strip()
    ar_genres = [g["name"] for g in ar_response.get("genres", [])]

    en_title = None
    en_overview = None
    en_genres = ar_genres

    if not ar_title or not ar_overview:
        try:
            en_response = _tmdb_get(f"/movie/{tmdb_id}", {"language": "en"})
            en_title = (en_response.get("title") or "").strip()
            en_overview = (en_response.get("overview") or "").strip()
            if not ar_genres:
                en_genres = [g["name"] for g in en_response.get("genres", [])]
        except Exception as e:
            print(f"    - API Error on English fallback fetch: {e}")
            pass

    final_title = ar_title or en_title or ar_response.get("original_title", "")
    final_overview = ar_overview or en_overview or ""

    return {
        "title": final_title,
        "overview": final_overview,
        "poster_path": ar_response.get("poster_path"),
        "backdrop_path": ar_response.get("backdrop_path"),
        "vote_average": ar_response.get("vote_average"),
        "runtime": ar_response.get("runtime"),
        "genres": json.dumps(en_genres if en_genres else ar_genres, ensure_ascii=False),
        "imdb_id": ar_response.get("imdb_id"),
    }

def main():
    print("========================================")
    print("  TMDB Arabic Metadata Migration Tool")
    print("========================================")
    
    db_url = get_db_url(get_database_url(), get_database_path())
    SessionLocal = init_db(db_url)
    
    with SessionLocal() as session:
        # Load all existing TMDB records
        movies = session.execute(select(TMDBMovie)).scalars().all()
        
        if not movies:
            print("No TMDB records found in the database. Nothing to migrate.")
            return

        total_movies = len(movies)
        print(f"Found {total_movies} total TMDB records.")
        
        processed = load_state()
        if processed:
            print(f"Resuming from state file: {len(processed)} records already migrated.")
            
        to_process = [m for m in movies if m.tmdb_id not in processed]
        print(f"Remaining to process: {len(to_process)}\n")
        
        if not to_process:
            print("All movies have already been migrated! Exiting.")
            return
            
        success_count = 0
        error_count = 0
        skip_count = 0
        
        start_time = time.time()
        
        for i, tmdb in enumerate(to_process, 1):
            print(f"[{i}/{len(to_process)}] Processing TMDB ID {tmdb.tmdb_id} (Current title: '{tmdb.title}')...")
            
            data = fetch_arabic_metadata(tmdb.tmdb_id)
            if data is None:
                print("    -> Failed to fetch metadata. Skipping.")
                error_count += 1
                continue
                
            # Update the existing TMDBMovie record fields only
            tmdb.title = data["title"]
            tmdb.overview = data["overview"]
            tmdb.poster_path = data["poster_path"]
            tmdb.backdrop_path = data["backdrop_path"]
            tmdb.vote_average = data["vote_average"]
            tmdb.runtime = data["runtime"]
            tmdb.genres = data["genres"]
            tmdb.imdb_id = data["imdb_id"]
            
            try:
                session.commit()
                processed.add(tmdb.tmdb_id)
                success_count += 1
                print(f"    -> Success: Updated to '{tmdb.title}'")
            except Exception as e:
                session.rollback()
                print(f"    -> Database save error: {e}")
                error_count += 1
                continue
                
            # Periodically save state in case of unexpected interrupt
            if success_count % 25 == 0:
                save_state(processed)
                
        # Final state save
        save_state(processed)
        
        duration = time.time() - start_time
        print("\n========================================")
        print("  Migration Complete")
        print("========================================")
        print(f"Total target       : {len(to_process)}")
        print(f"Successfully saved : {success_count}")
        print(f"Errors encountered : {error_count}")
        print(f"Time elapsed       : {duration:.2f} seconds")
        print("========================================")

if __name__ == '__main__':
    main()
