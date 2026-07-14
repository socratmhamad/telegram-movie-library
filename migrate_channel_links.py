"""
migrate_channel_links.py — Migrate movie Telegram links to a new channel.

When a Telegram channel gets banned or replaced, this script:
1. Updates the Library record with the new channel URL and numeric ID.
2. Scrapes the new channel for movie messages.
3. Matches scraped messages to existing Movie records (by TMDB, exact title, fuzzy title).
4. Replaces old TelegramMessage records with the new message IDs.

Usage:
    python migrate_channel_links.py --library-id 1 --new-channel "https://t.me/+XXXXX" --new-channel-id "1234567890"

Flags:
    --library-id        ID of the library to migrate (required)
    --new-channel       New Telegram channel URL or @handle (required)
    --new-channel-id    Numeric channel ID for private deep links (optional)
    --dry-run           Preview matches without writing to DB
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass, field

from rapidfuzz import fuzz
from sqlalchemy import select, delete
from telethon import TelegramClient

from config import settings
from database.models import (
    get_db_url,
    init_db,
    Library,
    Movie,
    TMDBMovie,
    TelegramMessage,
)


# ---------------------------------------------------------------------------
# Title cleaning (reused from deleted scraper/parser.py)
# ---------------------------------------------------------------------------

QUALITY_PATTERN = re.compile(
    r"\b(144p|240p|360p|480p|576p|720p|1080p|2160p|4k)\b", re.IGNORECASE
)
NOISE_PATTERNS = (
    re.compile(r"\b(?:hdrip|webrip|web-dl|bluray|blu-ray|brrip|dvdrip|mp4|mkv|avi)\b", re.IGNORECASE),
    re.compile(r"\b(?:x264|x265|h\.?264|h\.?265|hevc|aac|dual audio|multi audio)\b", re.IGNORECASE),
    re.compile(r"\b(?:download|watch|movie|movies|full movie|new link)\b", re.IGNORECASE),
    re.compile(r"\[?cinemamlt\]?", re.IGNORECASE),
    re.compile(r"https?://\S+", re.IGNORECASE),
    re.compile(r"@\w+"),
    re.compile(r"#[\w-]+"),
)


def clean_title(text: str) -> str:
    """Clean a Telegram message into a comparable movie title."""
    text = text.replace("_", " ")
    # Remove Arabic
    text = re.sub(r"[\u0600-\u06FF]+", " ", text)
    # Remove emojis / non-standard symbols
    text = re.sub(r"[^\w\s\.,!\?:\-\'\"()\[\]&]", " ", text)
    text = re.sub(r"[\[\]{}]", " ", text)
    text = QUALITY_PATTERN.sub(" ", text)
    for pattern in NOISE_PATTERNS:
        text = pattern.sub(" ", text)
    text = re.sub(r"[-|:]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .,-:;|")


def extract_title_from_message(message_text: str | None) -> str | None:
    """Extract the first valid title line from a Telegram message."""
    if not message_text:
        return None

    for line in message_text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip rating / IMDB lines
        if re.search(r"\b(?:imdb|rating|تقييم|التقييم|التقيم)\b", line, re.IGNORECASE):
            continue
        title = clean_title(line)
        # Validate
        if len(title) < 2 or len(title.split()) > 12:
            continue
        if not re.search(r"[A-Za-z0-9]", title):
            continue
        return title

    return None


# ---------------------------------------------------------------------------
# Matching engine
# ---------------------------------------------------------------------------

@dataclass
class MatchResult:
    movie_id: int
    movie_title: str
    new_message_id: int
    scraped_title: str
    method: str          # "tmdb_id", "exact", "fuzzy"
    score: float = 1.0   # 0-100 for fuzzy, 1.0 for exact/tmdb


@dataclass
class MigrationStats:
    total_scraped: int = 0
    matched_tmdb: int = 0
    matched_exact: int = 0
    matched_fuzzy: int = 0
    unmatched: int = 0
    unmatched_titles: list[str] = field(default_factory=list)


FUZZY_THRESHOLD = 80  # minimum fuzz ratio to accept


def build_match_indexes(session, library_id: int):
    """Build lookup structures from existing movies in library."""
    movies = session.execute(
        select(Movie, TMDBMovie)
        .outerjoin(TMDBMovie, Movie.tmdb_movie_id == TMDBMovie.id)
        .where(Movie.library_id == library_id)
    ).all()

    # title (lowered) -> movie_id
    title_index: dict[str, int] = {}
    # tmdb_id -> movie_id
    tmdb_index: dict[int, int] = {}
    # list of (movie_id, title) for fuzzy
    fuzzy_candidates: list[tuple[int, str]] = []

    for movie, tmdb in movies:
        lower = movie.title.strip().lower()
        title_index[lower] = movie.id
        fuzzy_candidates.append((movie.id, movie.title))
        if tmdb and tmdb.tmdb_id:
            tmdb_index[tmdb.tmdb_id] = movie.id

    return title_index, tmdb_index, fuzzy_candidates


def match_message(
    scraped_title: str,
    message_id: int,
    title_index: dict[str, int],
    tmdb_index: dict[int, int],
    fuzzy_candidates: list[tuple[int, str]],
    movie_titles: dict[int, str],
) -> MatchResult | None:
    """Try to match a scraped message to an existing movie."""
    lower = scraped_title.strip().lower()

    # 1. Exact title match
    if lower in title_index:
        mid = title_index[lower]
        return MatchResult(
            movie_id=mid,
            movie_title=movie_titles[mid],
            new_message_id=message_id,
            scraped_title=scraped_title,
            method="exact",
        )

    # 2. Fuzzy match
    best_score = 0.0
    best_id = None
    for mid, candidate_title in fuzzy_candidates:
        score = fuzz.ratio(lower, candidate_title.strip().lower())
        if score > best_score:
            best_score = score
            best_id = mid

    if best_id is not None and best_score >= FUZZY_THRESHOLD:
        return MatchResult(
            movie_id=best_id,
            movie_title=movie_titles[best_id],
            new_message_id=message_id,
            scraped_title=scraped_title,
            method="fuzzy",
            score=best_score,
        )

    return None


# ---------------------------------------------------------------------------
# Main migration logic
# ---------------------------------------------------------------------------

def _safe(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


async def migrate(
    library_id: int,
    new_channel: str,
    new_channel_id: str | None,
    dry_run: bool,
) -> None:
    db_url = get_db_url(settings.database_url, settings.database_path)
    SessionLocal = init_db(db_url)

    with SessionLocal() as session:
        library = session.execute(
            select(Library).where(Library.id == library_id)
        ).scalar_one_or_none()
        if library is None:
            print(f"ERROR: Library with id={library_id} not found.")
            sys.exit(1)

        print(f"Library: {library.name} (id={library.id})")
        print(f"  Old channel: {library.telegram_channel}")
        print(f"  New channel: {new_channel}")
        print()

        # Build match indexes
        title_index, tmdb_index, fuzzy_candidates = build_match_indexes(session, library_id)
        # movie_id -> title for display
        movie_titles = {mid: title for title, mid in
                        [(t, m) for m, t in fuzzy_candidates]}

        print(f"Loaded {len(fuzzy_candidates)} existing movies for matching.")
        print()

    # Scrape new channel
    print(f"Connecting to Telegram and scraping: {new_channel}")
    print("This may take a while for large channels...")
    print()

    client = TelegramClient(
        settings.telegram_session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )
    await client.start()

    resolved_channel_id = None
    scraped: list[tuple[str, int]] = []  # (title, message_id)
    count = 0
    try:
        # Auto-resolve channel entity to get ID
        try:
            entity = await client.get_entity(new_channel)
            # entity.id is usually positive, but strip -100 just in case
            entity_id_str = str(entity.id)
            if entity_id_str.startswith("-100"):
                entity_id_str = entity_id_str[4:]
            resolved_channel_id = entity_id_str
            print(f"Auto-resolved channel ID from Telegram: {resolved_channel_id}")
        except Exception as e:
            print(f"Warning: Could not auto-resolve channel ID via Telethon: {e}")

        async for message in client.iter_messages(new_channel, limit=None):
            count += 1
            if count % 500 == 0:
                print(f"  ... scanned {count} messages ...")

            title = extract_title_from_message(message.message)
            if title:
                scraped.append((title, message.id))
    finally:
        await client.disconnect()

    print(f"\nScraped {count} messages, found {len(scraped)} movie candidates.")
    print()

    # Match
    stats = MigrationStats(total_scraped=len(scraped))
    matches: list[MatchResult] = []

    for scraped_title, msg_id in scraped:
        result = match_message(
            scraped_title, msg_id,
            title_index, tmdb_index, fuzzy_candidates, movie_titles,
        )
        if result:
            matches.append(result)
            if result.method == "tmdb_id":
                stats.matched_tmdb += 1
            elif result.method == "exact":
                stats.matched_exact += 1
            else:
                stats.matched_fuzzy += 1
        else:
            stats.unmatched += 1
            stats.unmatched_titles.append(scraped_title)

    # Print results
    print("=" * 60)
    print("  MATCHING RESULTS")
    print("=" * 60)
    print(f"  Total scraped movies     : {stats.total_scraped}")
    print(f"  Matched (exact title)    : {stats.matched_exact}")
    print(f"  Matched (fuzzy)          : {stats.matched_fuzzy}")
    print(f"  Matched (TMDB ID)        : {stats.matched_tmdb}")
    print(f"  Unmatched                : {stats.unmatched}")
    print("=" * 60)
    print()

    if stats.unmatched > 0:
        print("Unmatched titles (first 20):")
        for title in stats.unmatched_titles[:20]:
            print(f"  - {_safe(title)}")
        print()

    # Show some fuzzy matches for review
    fuzzy_matches = [m for m in matches if m.method == "fuzzy"]
    if fuzzy_matches:
        print("Fuzzy matches (review these):")
        for m in fuzzy_matches[:20]:
            print(f"  [{m.score:.0f}%] \"{_safe(m.scraped_title)}\" -> \"{_safe(m.movie_title)}\"")
        print()

    if dry_run:
        print("DRY RUN — no database changes made.")
        return

    # Apply changes
    print("Applying changes to database...")
    with SessionLocal() as session:
        # 1. Update library record
        library = session.execute(
            select(Library).where(Library.id == library_id)
        ).scalar_one()

        library.telegram_channel = new_channel
        if new_channel_id:
            library.telegram_channel_id = new_channel_id
        elif resolved_channel_id:
            library.telegram_channel_id = resolved_channel_id

        # 2. Delete old telegram messages for matched movies
        matched_movie_ids = {m.movie_id for m in matches}
        if matched_movie_ids:
            session.execute(
                delete(TelegramMessage).where(
                    TelegramMessage.movie_id.in_(matched_movie_ids)
                )
            )

        # 3. Insert new telegram messages
        for m in matches:
            session.add(TelegramMessage(
                movie_id=m.movie_id,
                message_id=m.new_message_id,
            ))

        session.commit()

    print(f"Done. Updated {len(matches)} movie links and library channel info.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Migrate movie Telegram links to a new channel."
    )
    parser.add_argument(
        "--library-id", type=int, required=True,
        help="ID of the library to migrate",
    )
    parser.add_argument(
        "--new-channel", required=True,
        help="New Telegram channel URL or @handle",
    )
    parser.add_argument(
        "--new-channel-id", default=None,
        help="Numeric channel ID for private deep links (without -100 prefix)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview matches without writing to database",
    )
    args = parser.parse_args()

    asyncio.run(migrate(
        library_id=args.library_id,
        new_channel=args.new_channel,
        new_channel_id=args.new_channel_id,
        dry_run=args.dry_run,
    ))


if __name__ == "__main__":
    main()
