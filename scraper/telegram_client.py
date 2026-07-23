import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings


@asynccontextmanager
async def get_telegram_client() -> AsyncIterator[TelegramClient]:
    """Create, authenticate, and cleanly disconnect a Telethon client."""
    if settings.telegram_api_id <= 0 or not settings.telegram_api_hash:
        raise RuntimeError(
            "Missing required environment variables for Telegram: TELEGRAM_API_ID and TELEGRAM_API_HASH must be configured."
        )

    if settings.telegram_session_string:
        session = StringSession(settings.telegram_session_string)
    else:
        session = settings.telegram_session_name

    client = TelegramClient(
        session,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )

    bot_token = settings.telegram_bot_token

    if bot_token:
        await client.start(bot_token=bot_token)
    else:
        await client.connect()
        if not await client.is_user_authorized():
            if not sys.stdin.isatty():
                await client.disconnect()
                raise RuntimeError(
                    "Telegram client is not authorized and interactive terminal input (stdin) is unavailable.\n"
                    "To fix this on Render/cloud server:\n"
                    "  1. Set TELEGRAM_SESSION_STRING in your environment variables (run 'python export_session_string.py' locally to generate it).\n"
                    "  OR\n"
                    "  2. Set TELEGRAM_BOT_TOKEN in your environment variables (if using a Telegram bot)."
                )
            await client.start()

    try:
        yield client
    finally:
        await client.disconnect()
