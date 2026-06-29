from __future__ import annotations

import sys

from tmdb_service import build_poster_url, get_movie_details, search_movie


def main() -> None:
    title = " ".join(sys.argv[1:]).strip()
    if not title:
        title = input("Movie title: ").strip()

    try:
        movie = search_movie(title)
        if not movie:
            print(f"No TMDB result found for: {title}")
            return

        details = get_movie_details(int(movie["tmdb_id"]))
    except RuntimeError as exc:
        print(exc)
        return

    print(f"TMDB ID: {movie['tmdb_id']}")
    print(f"Title: {movie['title']}")
    print(f"Rating: {details['vote_average']}")
    print(f"Release Date: {movie['release_date']}")
    print(f"Poster URL: {build_poster_url(details['poster_path']) or 'N/A'}")


if __name__ == "__main__":
    main()
