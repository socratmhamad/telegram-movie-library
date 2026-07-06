import asyncio
import time

from sqlalchemy import select

from config import settings
from scraper.database import MovieDatabase
from scraper.scraper import TelegramMovieScraper, ScrapeStats
from scraper.telegram_client import get_telegram_client
from database.models import get_db_url, init_db, Library


def _safe(text: str) -> str:
    """Return a console-safe version of *text* (handles Windows cp1252)."""
    return text.encode("ascii", errors="replace").decode("ascii")


async def run() -> None:
    db_url = get_db_url(settings.database_url, settings.database_path)
    database = MovieDatabase(db_url)
    
    SessionLocal = init_db(db_url)
    with SessionLocal() as session:
        libraries = session.execute(select(Library).where(Library.is_active == True)).scalars().all()
        active_libs = [{"id": lib.id, "name": lib.name, "channel": lib.telegram_channel} for lib in libraries]

    if not active_libs:
        print("No active libraries found in the database. Please add a library first.")
        return

    print(f"Found {len(active_libs)} active libraries. Starting multi-library scrape...")
    print()

    global_stats = ScrapeStats()
    start_time = time.time()

    async with get_telegram_client() as client:
        for lib in active_libs:
            library_id = lib["id"]
            telegram_channel = lib["channel"]
            library_name = lib["name"]

            print("=" * 60)
            print(f"Scraping library: {library_name} ({telegram_channel})")
            print("=" * 60)

            # Load message IDs already in the database for this library
            known_ids = database.get_known_message_ids(library_id)
            print(f"Found {len(known_ids)} existing Telegram message(s) for this library.")
            print()

            scraper = TelegramMovieScraper(client, telegram_channel)

            lib_stats = ScrapeStats()

            try:
                async for message in client.iter_messages(telegram_channel, limit=None):
                    lib_stats.total_messages_scanned += 1
                    global_stats.total_messages_scanned += 1

                    if lib_stats.total_messages_scanned % 500 == 0:
                        print(f"  ... scanned {lib_stats.total_messages_scanned} messages so far ...")

                    if message.id in known_ids:
                        lib_stats.duplicates_skipped += 1
                        global_stats.duplicates_skipped += 1
                        continue

                    record = scraper._parse_message(message)
                    if not record:
                        continue

                    lib_stats.total_movies_found += 1
                    global_stats.total_movies_found += 1

                    if database.save_movie_message(record.title, record.message_id, library_id):
                        lib_stats.new_movies_added += 1
                        global_stats.new_movies_added += 1
                        print(f"  [NEW] {_safe(record.title)} (msg #{record.message_id}, quality: {record.quality or 'unknown'})")
            except Exception as e:
                print(f"  [ERROR] Failed to scrape {telegram_channel}: {e}")
                continue

            print(f"\nFinished library: {library_name}")
            print(f"  -> Messages scanned: {lib_stats.total_messages_scanned}")
            print(f"  -> New movies added: {lib_stats.new_movies_added}\n")

    elapsed = time.time() - start_time

    print("=" * 60)
    print("  GLOBAL SCRAPING COMPLETE")
    print("=" * 60)
    print(f"  Total Telegram messages scanned : {global_stats.total_messages_scanned}")
    print(f"  Total movies imported (parsed)  : {global_stats.total_movies_found}")
    print(f"  Total duplicates skipped        : {global_stats.duplicates_skipped}")
    print(f"  Total new movies added          : {global_stats.new_movies_added}")
    print(f"  Time elapsed                    : {elapsed:.1f}s")
    print("=" * 60)
    print()
    print(f"Database: {settings.database_path}")


if __name__ == "__main__":
    asyncio.run(run())
