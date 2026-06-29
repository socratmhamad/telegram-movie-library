from __future__ import annotations

import asyncio

from config import settings
from scraper.database import MovieDatabase
from scraper.scraper import TelegramMovieScraper
from scraper.telegram_client import get_telegram_client


async def run() -> None:
    database = MovieDatabase(settings.database_path)

    async with get_telegram_client() as client:
        scraper = TelegramMovieScraper(client, settings.telegram_channel)
        saved_count = 0

        async for record in scraper.iter_records(settings.message_limit):
            print(f"Movie Title: {record.title}")
            print(f"Quality: {record.quality or 'unknown'}")
            print(f"Message ID: {record.message_id}")
            print()

            if database.save_movie_message(record.title, record.message_id):
                saved_count += 1

    print(f"Saved {saved_count} Telegram message records to {settings.database_path}")


if __name__ == "__main__":
    asyncio.run(run())
