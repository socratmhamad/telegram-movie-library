from __future__ import annotations

import concurrent.futures
import json
import re
import sys
import threading
import time
from typing import Any

import requests

from config import settings
from scraper.database import MovieDatabase
from database.models import get_db_url
from sqlalchemy import text
from tmdb_service import _choose_best_match

# Regex patterns for cleaning titles
YEAR_PATTERN = re.compile(r"\b((?:19|20)\d{2})\b")
QUALITY_PATTERN = re.compile(
    r"\b(?:240p|360p|480p|576p|720p|1080p|2160p|4k|1080|720|1080i|720i)\b", 
    re.IGNORECASE
)
NOISE_PATTERNS = [
    re.compile(r"\b(?:hdrip|webrip|web-dl|bluray|brrip|dvdrip|dvd|hd|web|rip|ts|cam|tc|scr|screener)\b", re.IGNORECASE),
    re.compile(r"\b(?:x264|x265|h\.?264|h\.?265|hevc|aac|ac3|dts|dd5\.?1|dual[- ]audio|multi[- ]audio|hindi|dubbed|subbed|eng|esub|hardsub)\b", re.IGNORECASE),
    re.compile(r"\b(?:download|watch|movie|movies|full movie|new link|link|nf|netflix|amzn|amazon|hulu|disney|dsnp|apple|atvp|hbom|hbo|columbia|starwars|episode)\b", re.IGNORECASE),
]
EXTENSION_PATTERN = re.compile(r"\.(?:mp4|mkv|avi|flv|mov|wmv|mpg|mpeg|webm|3gp)$", re.IGNORECASE)


def _safe(text: str) -> str:
    """Return a console-safe version of *text* (handles Windows cp1252)."""
    return text.encode("ascii", errors="replace").decode("ascii")


def clean_title_and_extract_year(raw_title: str) -> tuple[str, int | None]:
    """
    Clean movie titles before searching TMDB and extract release year if available.
    """
    title = raw_title.strip()
    
    # 1. Remove file extensions (e.g. .mp4, .mkv)
    title = EXTENSION_PATTERN.sub("", title)
    
    # 2. Extract and remove year (19xx or 20xx)
    years = YEAR_PATTERN.findall(title)
    year = None
    if years:
        year = int(years[-1])
        title = YEAR_PATTERN.sub(" ", title)
        
    # 3. Clean quality and noise patterns
    title = QUALITY_PATTERN.sub(" ", title)
    for pattern in NOISE_PATTERNS:
        title = pattern.sub(" ", title)
        
    # 4. Clean list prefix numbers like "1. Divergent" -> "Divergent"
    title = re.sub(r"^\d+\s*[\.\-\)]\s+", " ", title)
    
    # Split CamelCase (e.g. TheWomanKing -> The Woman King)
    title = re.sub(r'([a-z])([A-Z])', r'\1 \2', title)
    
    # Remove dots entirely (e.g. M.3.G.A.N -> M3GAN)
    title = title.replace(".", "")
    
    # 5. Clean punctuation, replacing separators with spaces
    title = re.sub(r"[\_\-\:\/\|\\*\+]", " ", title)
    title = re.sub(r"[\[\]{}()\"\'“”’`~!?@#\$%\^&;]", " ", title)
    
    # 6. Normalize whitespace
    title = re.sub(r"\s+", " ", title).strip()
    
    return title, year


class TMDBClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.base_url = "https://api.themoviedb.org/3"
        self.request_lock = threading.Lock()
        
    def request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        all_params = {"api_key": self.api_key, **params}
        
        max_retries = 5
        backoff = 1.0
        
        for attempt in range(max_retries):
            try:
                # Thread-safe request pacing
                with self.request_lock:
                    time.sleep(0.05)
                
                response = self.session.get(url, params=all_params, timeout=15)
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after and retry_after.isdigit() else backoff
                    print(f"  [Rate Limited] Waiting {sleep_time}s on attempt {attempt+1}...")
                    time.sleep(sleep_time)
                    backoff *= 2
                    continue
                    
                # Check for server errors
                if response.status_code >= 500:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as exc:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"TMDB request to {path} failed: {exc}") from exc
                time.sleep(backoff)
                backoff *= 2
                continue
                
        raise RuntimeError(f"TMDB request to {path} failed after {max_retries} retries")

    def search_movie(self, title: str, year: int | None = None) -> dict[str, Any] | None:
        query = title.strip()
        if not query:
            return None
            
        params = {
            "query": query,
            "include_adult": "false",
        }
        if year:
            params["year"] = str(year)
            
        try:
            response = self.request("/search/movie", params)
        except Exception:
            return None
            
        results = response.get("results", [])
        if not results:
            return None
            
        best_match = _choose_best_match(query, results, expected_year=year)
        return {
            "tmdb_id": best_match.get("id"),
            "title": best_match.get("title"),
            "original_title": best_match.get("original_title"),
            "release_date": best_match.get("release_date"),
        }

    def get_movie_details(self, tmdb_id: int) -> dict[str, Any]:
        response = self.request(f"/movie/{tmdb_id}", {})
        return {
            "poster_path": response.get("poster_path"),
            "backdrop_path": response.get("backdrop_path"),
            "overview": response.get("overview"),
            "vote_average": response.get("vote_average"),
            "runtime": response.get("runtime"),
            "genres": [genre["name"] for genre in response.get("genres", [])],
            "imdb_id": response.get("imdb_id"),
        }


class Stats:
    def __init__(self, total_to_process: int, already_linked: int):
        self.total_to_process = total_to_process
        self.already_linked = already_linked
        self.processed = 0
        self.matched = 0
        self.not_found = 0
        self.errors = 0
        self.lock = threading.Lock()

    def increment_processed(self) -> int:
        with self.lock:
            self.processed += 1
            return self.processed

    def increment_matched(self):
        with self.lock:
            self.matched += 1

    def increment_not_found(self):
        with self.lock:
            self.not_found += 1

    def increment_errors(self):
        with self.lock:
            self.errors += 1


def process_movie(
    movie: Any, 
    client: TMDBClient, 
    database: MovieDatabase, 
    stats: Stats, 
    db_lock: threading.Lock
) -> None:
    raw_title = movie["title"]
    movie_id = int(movie["id"])
    
    cleaned_title, year = clean_title_and_extract_year(raw_title)
    year_str = str(year) if year else "N/A"
    
    idx = stats.increment_processed()
    remaining = stats.total_to_process - idx
    
    safe_raw = _safe(raw_title)
    safe_clean = _safe(cleaned_title)
    
    log_msg = f"[{idx}/{stats.total_to_process}] Processing: \"{safe_raw}\"\n"
    log_msg += f"  Cleaned: \"{safe_clean}\" | Year: {year_str}\n"

    try:
        tmdb_result = None
        if cleaned_title:
            tmdb_result = client.search_movie(cleaned_title, year=year)
            if not tmdb_result and year:
                log_msg += f"  (No match with year {year}; trying search without year...)\n"
                tmdb_result = client.search_movie(cleaned_title)

        if not tmdb_result:
            stats.increment_not_found()
            log_msg += "  Matched: No (Not Found)\n"
            sys.stdout.write(log_msg + "\n")
            sys.stdout.flush()
            
            # Print periodic progress
            if idx % 50 == 0 or idx == stats.total_to_process:
                with stats.lock:
                    matched = stats.matched
                    not_found = stats.not_found
                    errors = stats.errors
                sys.stdout.write(f"--- Progress: {idx}/{stats.total_to_process} processed | Matched: {matched} | Not Found: {not_found} | Errors: {errors} | Remaining: {remaining} ---\n\n")
                sys.stdout.flush()
            return

        # Fetch details
        details = client.get_movie_details(int(tmdb_result["tmdb_id"]))
        tmdb_movie = {
            **tmdb_result,
            **details,
        }
        
        # Save and link in DB
        with db_lock:
            tmdb_movie_id = database.save_tmdb_movie(tmdb_movie)
            database.link_movie_to_tmdb(movie_id, tmdb_movie_id)

        stats.increment_matched()
        safe_tmdb_title = _safe(tmdb_result['title'])
        log_msg += f"  Matched: Yes -> \"{safe_tmdb_title}\" (TMDB ID: {tmdb_result['tmdb_id']}, Release Date: {tmdb_result.get('release_date') or 'N/A'})\n"
        sys.stdout.write(log_msg + "\n")
        sys.stdout.flush()

    except Exception as exc:
        stats.increment_errors()
        log_msg += f"  Error: {exc}\n"
        sys.stdout.write(log_msg + "\n")
        sys.stdout.flush()

    # Print periodic progress
    if idx % 50 == 0 or idx == stats.total_to_process:
        with stats.lock:
            matched = stats.matched
            not_found = stats.not_found
            errors = stats.errors
        sys.stdout.write(f"--- Progress: {idx}/{stats.total_to_process} processed | Matched: {matched} | Not Found: {not_found} | Errors: {errors} | Remaining: {remaining} ---\n\n")
        sys.stdout.flush()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    db_url = get_db_url(settings.database_url, settings.database_path)
    database = MovieDatabase(db_url)

    # Count already linked movies
    with database._connection() as session:
        already_linked_count = session.scalar(
            text("SELECT COUNT(*) FROM movies WHERE tmdb_movie_id IS NOT NULL")
        )
        total_movies_count = session.scalar(text("SELECT COUNT(*) FROM movies"))

    to_process = database.get_movies_without_tmdb()
    total_to_process = len(to_process)

    print("=" * 60)
    print("  PRODUCTION CONCURRENT TMDB UPDATER START")
    print("=" * 60)
    print(f"  Total movies in DB       : {total_movies_count}")
    print(f"  Already linked to TMDB   : {already_linked_count}")
    print(f"  Unlinked to process      : {total_to_process}")
    print(f"  Concurrency Level        : 4 Threads")
    print("=" * 60)
    print()

    tmdb_key = settings.tmdb_api_key
    if not tmdb_key:
        print("Error: Missing TMDB_API_KEY environment variable.")
        sys.exit(1)

    client = TMDBClient(tmdb_key)
    stats = Stats(total_to_process, already_linked_count)
    db_lock = threading.Lock()
    start_time = time.time()

    # Run with 4 threads concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(process_movie, movie, client, database, stats, db_lock)
            for movie in to_process
        ]
        concurrent.futures.wait(futures)

    elapsed = time.time() - start_time

    # Final report
    print("=" * 60)
    print("  TMDB UPDATE PROCESS COMPLETE")
    print("=" * 60)
    print(f"  Total movies processed  : {stats.processed}")
    print(f"  Successfully matched    : {stats.matched}")
    print(f"  Not found               : {stats.not_found}")
    print(f"  Errors/Skipped          : {stats.errors}")
    print(f"  Already linked          : {already_linked_count}")
    print(f"  Total execution time    : {elapsed:.1f} seconds")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
