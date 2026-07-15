from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import time

from dotenv import load_dotenv
from rapidfuzz import fuzz


TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
REQUEST_TIMEOUT_SECONDS = 15
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def search_movie(title: str, year: int | str | None = None) -> dict[str, Any] | None:
    """
    Search TMDB by movie title and return the best matching result.

    Returned keys:
    - tmdb_id
    - title
    - original_title
    - release_date
    """
    query = title.strip()
    if not query:
        return None

    params = {
        "query": query,
        "include_adult": "false",
    }
    if year:
        params["year"] = str(year)

    response = _tmdb_get("/search/movie", params)
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


def get_movie_details(tmdb_id: int, language: str | None = None) -> dict[str, Any]:
    """
    Fetch detailed TMDB metadata for a movie.

    Returned keys:
    - poster_path
    - backdrop_path
    - overview
    - vote_average
    - runtime
    - genres
    - imdb_id
    """
    params = {}
    if language:
        params["language"] = language
    response = _tmdb_get(f"/movie/{tmdb_id}", params)
    return {
        "poster_path": response.get("poster_path"),
        "backdrop_path": response.get("backdrop_path"),
        "overview": response.get("overview"),
        "vote_average": response.get("vote_average"),
        "runtime": response.get("runtime"),
        "genres": [genre["name"] for genre in response.get("genres", [])],
        "imdb_id": response.get("imdb_id"),
    }



def build_poster_url(poster_path: str | None) -> str | None:
    if not poster_path:
        return None

    return f"{TMDB_IMAGE_BASE_URL}{poster_path}"


def _tmdb_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("Missing required environment variable: TMDB_API_KEY")

    # Baseline rate limit: wait 0.1s before each request to respect limits
    time.sleep(0.1)

    query_params = {"api_key": api_key, **params}
    url = f"{TMDB_API_BASE_URL}{path}?{urlencode(query_params)}"
    request = Request(url, headers={"Accept": "application/json"})

    max_retries = 5
    backoff = 1.0

    for attempt in range(max_retries):
        try:
            with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            # Retry on rate limit (429) or server errors (5xx)
            if exc.code == 429 or exc.code >= 500:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"TMDB request failed with status {exc.code} after {max_retries} attempts") from exc
                
                # Check for Retry-After header
                retry_after = exc.headers.get("Retry-After")
                sleep_time = float(retry_after) if retry_after and retry_after.isdigit() else backoff
                time.sleep(sleep_time)
                backoff *= 2
                continue
            raise RuntimeError(f"TMDB request failed with status {exc.code}") from exc
        except (URLError, Exception) as exc:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Could not connect to TMDB after {max_retries} attempts: {exc}") from exc
            time.sleep(backoff)
            backoff *= 2
            continue


def _choose_best_match(query: str, results: list[dict[str, Any]], expected_year: int | str | None = None) -> dict[str, Any]:
    normalized_query = _normalize_title(query)
    
    if expected_year:
        try:
            expected_year = int(expected_year)
        except ValueError:
            expected_year = None

    def score(result: dict[str, Any]) -> tuple[float, int, float]:
        title = _normalize_title(str(result.get("title") or ""))
        original_title = _normalize_title(str(result.get("original_title") or ""))
        
        score_title = fuzz.ratio(normalized_query, title)
        score_orig = fuzz.ratio(normalized_query, original_title)
        match_score = max(score_title, score_orig)
        
        year_score = 0
        if expected_year:
            release_date = result.get("release_date")
            if release_date and len(release_date) >= 4:
                try:
                    res_year = int(release_date[:4])
                    if res_year == expected_year:
                        year_score = 2
                    elif abs(res_year - expected_year) == 1:
                        year_score = 1
                except ValueError:
                    pass
                    
        popularity = float(result.get("popularity") or 0)
        return match_score, year_score, popularity

    return max(results, key=score)


def _normalize_title(title: str) -> str:
    normalized = title.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()
