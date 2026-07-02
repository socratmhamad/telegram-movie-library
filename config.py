from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    telegram_api_id: int
    telegram_api_hash: str
    telegram_channel: str
    telegram_session_name: str
    message_limit: int
    database_path: Path
    database_url: str | None
    tmdb_api_key: str | None


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer") from exc


def _path_env(name: str, default: Path) -> Path:
    raw_path = Path(os.getenv(name, default))
    if raw_path.is_absolute():
        return raw_path

    return BASE_DIR / raw_path


settings = Settings(
    telegram_api_id=_int_env("TELEGRAM_API_ID", 0),
    telegram_api_hash=_required_env("TELEGRAM_API_HASH"),
    telegram_channel=_required_env("TELEGRAM_CHANNEL"),
    telegram_session_name=os.getenv("TELEGRAM_SESSION_NAME", "telegram_movies"),
    message_limit=_int_env("MESSAGE_LIMIT", 100),
    database_path=_path_env("DATABASE_PATH", Path("database") / "movies.db"),
    database_url=os.getenv("DATABASE_URL"),
    tmdb_api_key=os.getenv("TMDB_API_KEY"),
)

if settings.telegram_api_id <= 0:
    raise RuntimeError("Missing required environment variable: TELEGRAM_API_ID")
