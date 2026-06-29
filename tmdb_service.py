from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv


TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
REQUEST_TIMEOUT_SECONDS = 15
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def search_movie(title: str) -> dict[str, Any] | None:
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

    response = _tmdb_get(
        "/search/movie",
        {
            "query": query,
            "include_adult": "false",
        },
    )
    results = response.get("results", [])
    if not results:
        return None

    best_match = _choose_best_match(query, results)
    return {
        "tmdb_id": best_match.get("id"),
        "title": best_match.get("title"),
        "original_title": best_match.get("original_title"),
        "release_date": best_match.get("release_date"),
    }


def get_movie_details(tmdb_id: int) -> dict[str, Any]:
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
    response = _tmdb_get(f"/movie/{tmdb_id}", {})
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

    query_params = {"api_key": api_key, **params}
    url = f"{TMDB_API_BASE_URL}{path}?{urlencode(query_params)}"
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"TMDB request failed with status {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not connect to TMDB: {exc.reason}") from exc


def _choose_best_match(query: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_query = _normalize_title(query)

    def score(result: dict[str, Any]) -> tuple[int, float]:
        title = _normalize_title(str(result.get("title") or ""))
        original_title = _normalize_title(str(result.get("original_title") or ""))
        exact_match_score = int(title == normalized_query or original_title == normalized_query)
        popularity = float(result.get("popularity") or 0)
        return exact_match_score, popularity

    return max(results, key=score)


def _normalize_title(title: str) -> str:
    normalized = title.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()
