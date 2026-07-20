from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")


def get_app_env() -> str:
    """Return the current application environment (development | production)."""
    return os.getenv("APP_ENV", "development").lower()


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
    """Get the database URL from the environment for SQLAlchemy.

    Only returns the URL when APP_ENV=production so local development
    always falls back to the local SQLite database.
    """
    if get_app_env() != "production":
        return None
    return os.getenv("DATABASE_URL")


def get_telegram_channel_id() -> str | None:
    """Return the numeric Telegram channel ID (without the ``-100`` prefix).

    Used to build ``https://t.me/c/{channel_id}/{message_id}`` deep links.
    """
    return os.getenv("TELEGRAM_CHANNEL_ID") or None
