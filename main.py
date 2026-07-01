from __future__ import annotations

import asyncio
import time

from config import settings
from scraper.database import MovieDatabase
from scraper.scraper import TelegramMovieScraper, ScrapeStats
from scraper.telegram_client import get_telegram_client


def _safe(text: str) -> str:
    """Return a console-safe version of *text* (handles Windows cp1252)."""
    return text.encode("ascii", errors="replace").decode("ascii")


async def run() -> None:
    database = MovieDatabase(settings.database_path)

    # Load all message IDs already in the database for incremental scraping
    known_ids = database.get_known_message_ids()
    print(f"Found {len(known_ids)} existing Telegram message(s) in the database.")
    print()

    stats = ScrapeStats()
    start_time = time.time()

    async with get_telegram_client() as client:
        scraper = TelegramMovieScraper(client, settings.telegram_channel)

        # Fetch ALL messages from the channel (limit=None)
        print(f"Scraping full channel history: {settings.telegram_channel}")
        print("This may take a while for channels with thousands of messages...")
        print()

        async for message in client.iter_messages(settings.telegram_channel, limit=None):
            stats.total_messages_scanned += 1

            # Progress indicator every 500 messages
            if stats.total_messages_scanned % 500 == 0:
                print(f"  ... scanned {stats.total_messages_scanned} messages so far ...")

            # Skip already-imported messages
            if message.id in known_ids:
                stats.duplicates_skipped += 1
                continue

            # Try to parse as a movie
            record = scraper._parse_message(message)
            if not record:
                continue

            stats.total_movies_found += 1

            # Save to database
            if database.save_movie_message(record.title, record.message_id):
                stats.new_movies_added += 1
                print(f"  [NEW] {_safe(record.title)} (msg #{record.message_id}, quality: {record.quality or 'unknown'})")

    elapsed = time.time() - start_time

    # Final report
    print()
    print("=" * 60)
    print("  SCRAPING COMPLETE")
    print("=" * 60)
    print(f"  Total Telegram messages scanned : {stats.total_messages_scanned}")
    print(f"  Total movies imported (parsed)  : {stats.total_movies_found}")
    print(f"  Total duplicates skipped        : {stats.duplicates_skipped}")
    print(f"  Total new movies added          : {stats.new_movies_added}")
    print(f"  Time elapsed                    : {elapsed:.1f}s")
    print("=" * 60)
    print()
    print(f"Database: {settings.database_path}")


if __name__ == "__main__":
    asyncio.run(run())
