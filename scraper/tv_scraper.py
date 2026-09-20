from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator

from telethon import TelegramClient
from telethon.tl.custom.message import Message

from scraper.tv_parser import parse_series_message, parse_bulk_series_message


@dataclass(frozen=True)
class SeriesRecord:
    title: str
    telegram_link: str | None
    message_id: int

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "telegram_link": self.telegram_link,
            "message_id": self.message_id,
        }


@dataclass
class SeriesScrapeStats:
    """Tracks statistics for a TV series scraping run."""
    total_messages_scanned: int = 0
    total_series_found: int = 0
    duplicates_skipped: int = 0
    new_series_added: int = 0


class TelegramSeriesScraper:
    """Reads channel messages and converts TV series posts into structured records."""

    def __init__(self, client: TelegramClient, channel: str) -> None:
        self.client = client
        self.channel = channel

    async def scrape(self, limit: int | None = None) -> list[SeriesRecord]:
        return [record async for record in self.iter_records(limit)]

    async def iter_records(
        self,
        limit: int | None = None,
        known_message_ids: set[int] | None = None,
    ) -> AsyncIterator[SeriesRecord]:
        """Iterate over channel messages and yield series records.

        Args:
            limit: Maximum number of Telegram messages to fetch.
                   ``None`` fetches the entire channel history.
            known_message_ids: Set of Telegram message IDs already processed.
                               Messages whose ID appears in this set are
                               silently skipped.
        """
        if known_message_ids is None:
            known_message_ids = set()

        async for message in self.client.iter_messages(self.channel, limit=limit):
            if message.id in known_message_ids:
                continue

            record = self._parse_message(message)
            if record:
                yield record

    def _parse_message(self, message: Message) -> SeriesRecord | None:
        parsed = parse_series_message(message.message)
        if not parsed:
            return None

        return SeriesRecord(
            title=parsed.title,
            telegram_link=parsed.telegram_link,
            message_id=message.id,
        )

    def _parse_message_multi(self, message: Message) -> list[SeriesRecord]:
        """Parse a message that may contain multiple series entries.

        Tries the bulk parser first. If the message does not match the bulk
        format, falls back to the single-entry parser.
        """
        bulk = parse_bulk_series_message(message.message)
        if bulk:
            return [
                SeriesRecord(
                    title=p.title,
                    telegram_link=p.telegram_link,
                    message_id=message.id,
                )
                for p in bulk
            ]

        # Fallback: single-entry parse
        single = self._parse_message(message)
        return [single] if single else []
