from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from telethon import TelegramClient

from config import settings


@asynccontextmanager
async def get_telegram_client() -> AsyncIterator[TelegramClient]:
    """Create, authenticate, and cleanly disconnect a Telethon client."""
    client = TelegramClient(
        settings.telegram_session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )

    await client.start()
    try:
        yield client
    finally:
        await client.disconnect()
