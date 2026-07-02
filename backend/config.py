from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")


def get_database_path() -> Path:
    """Resolve the database path from the environment.

    Keeps the backend independent of the scraper's ``config.py`` so it can
    start without Telegram credentials.
    """
    raw = Path(os.getenv("DATABASE_PATH", str(Path("database") / "movies.db")))
    if raw.is_absolute():
        return raw
    return _BASE_DIR / raw


def get_database_url() -> str | None:
    """Get the database URL from the environment for SQLAlchemy."""
    return os.getenv("DATABASE_URL")


def get_telegram_channel_id() -> str | None:
    """Return the numeric Telegram channel ID (without the ``-100`` prefix).

    Used to build ``https://t.me/c/{channel_id}/{message_id}`` deep links.
    """
    return os.getenv("TELEGRAM_CHANNEL_ID") or None
