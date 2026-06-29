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


class TelegramMovieScraper:
    """Reads channel messages and converts movie posts into structured records."""

    def __init__(self, client: TelegramClient, channel: str) -> None:
        self.client = client
        self.channel = channel

    async def scrape(self, limit: int) -> list[MovieRecord]:
        return [record async for record in self.iter_records(limit)]

    async def iter_records(self, limit: int) -> AsyncIterator[MovieRecord]:
        async for message in self.client.iter_messages(self.channel, limit=limit):
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
