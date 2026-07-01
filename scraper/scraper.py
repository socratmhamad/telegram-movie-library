from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator

from telethon import TelegramClient
from telethon.tl.custom.message import Message

from scraper.parser import parse_movie_message


@dataclass(frozen=True)
class MovieRecord:
    title: str
    quality: str | None
    message_id: int

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "quality": self.quality,
            "message_id": self.message_id,
        }


@dataclass
class ScrapeStats:
    """Tracks statistics for a scraping run."""
    total_messages_scanned: int = 0
    total_movies_found: int = 0
    duplicates_skipped: int = 0
    new_movies_added: int = 0


class TelegramMovieScraper:
    """Reads channel messages and converts movie posts into structured records."""

    def __init__(self, client: TelegramClient, channel: str) -> None:
        self.client = client
        self.channel = channel

    async def scrape(self, limit: int | None = None) -> list[MovieRecord]:
        return [record async for record in self.iter_records(limit)]

    async def iter_records(
        self,
        limit: int | None = None,
        known_message_ids: set[int] | None = None,
    ) -> AsyncIterator[MovieRecord]:
        """Iterate over channel messages and yield movie records.

        Args:
            limit: Maximum number of Telegram messages to fetch.
                   ``None`` fetches the entire channel history.
            known_message_ids: Set of Telegram message IDs already stored
                               in the database.  Messages whose ID appears
                               in this set are silently skipped so the
                               caller never receives duplicates.
        """
        if known_message_ids is None:
            known_message_ids = set()

        async for message in self.client.iter_messages(self.channel, limit=limit):
            if message.id in known_message_ids:
                continue

            record = self._parse_message(message)
            if record:
                yield record

    def _parse_message(self, message: Message) -> MovieRecord | None:
        parsed_movie = parse_movie_message(message.message)
        if not parsed_movie:
            return None

        return MovieRecord(
            title=parsed_movie.title,
            quality=parsed_movie.quality,
            message_id=message.id,
        )
