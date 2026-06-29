from __future__ import annotations

import sys

from config import settings
from scraper.database import MovieDatabase
from tmdb_service import get_movie_details, search_movie


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    database = MovieDatabase(settings.database_path)
    movies = database.get_movies_without_tmdb()

    processed_count = 0
    matched_count = 0
    skipped_count = 0

    for movie in movies:
        processed_count += 1
        title = movie["title"]

        print(f"Movie: {title}")

        try:
            tmdb_result = search_movie(title)
            if not tmdb_result:
                skipped_count += 1
                print("Matched: No")
                print("TMDB ID: N/A")
                print()
                continue

            details = get_movie_details(int(tmdb_result["tmdb_id"]))
            tmdb_movie = {
                **tmdb_result,
                **details,
            }
            tmdb_movie_id = database.save_tmdb_movie(tmdb_movie)
            database.link_movie_to_tmdb(int(movie["id"]), tmdb_movie_id)

            matched_count += 1
            print("Matched: Yes")
            print(f"TMDB ID: {tmdb_result['tmdb_id']}")
            print()
        except (RuntimeError, TypeError, ValueError) as exc:
            skipped_count += 1
            print("Matched: No")
            print("TMDB ID: N/A")
            print(f"Error: {exc}")
            print()

    print(f"Movies processed: {processed_count}")
    print(f"Movies matched: {matched_count}")
    print(f"Movies skipped: {skipped_count}")


if __name__ == "__main__":
    main()
