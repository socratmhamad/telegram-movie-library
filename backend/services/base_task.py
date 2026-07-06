import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import get_database_url, get_database_path
from database.models import get_db_url

@dataclass
class TaskProgress:
    status: str = "idle"  # idle, running, completed, error
    mode: str = ""        # import, update_links
    target_channel: str = ""
    total_scanned: int = 0
    matched_movies: int = 0
    updated_links: int = 0
    failed_updates: int = 0
    missing_movies: List[Dict[str, Any]] = field(default_factory=list)
    new_movies_added: int = 0
    tmdb_lookups_completed: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "target_channel": self.target_channel,
            "total_scanned": self.total_scanned,
            "matched_movies": self.matched_movies,
            "updated_links": self.updated_links,
            "failed_updates": self.failed_updates,
            "missing_movies": self.missing_movies,
            "new_movies_added": self.new_movies_added,
            "tmdb_lookups_completed": self.tmdb_lookups_completed,
            "execution_time": (self.end_time or time.time()) - self.start_time if self.start_time else 0.0,
            "error_message": self.error_message,
        }

class BaseTelegramTask:
    def __init__(self):
        self.progress = TaskProgress()
        db_url = get_db_url(get_database_url(), get_database_path())
        
        engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=engine)
        
        self._current_task: asyncio.Task | None = None

    def get_status(self) -> Dict[str, Any]:
        return self.progress.to_dict()

    async def test_connection(self, channel: str) -> tuple[bool, str | None]:
        """Tests if the provided channel is accessible and returns its numeric ID."""
        from scraper.telegram_client import get_telegram_client
        try:
            async with get_telegram_client() as client:
                entity = await client.get_entity(channel)
                
                # Extract numeric ID and strip -100 prefix if present
                channel_id = str(entity.id)
                if channel_id.startswith('-100'):
                    channel_id = channel_id[4:]
                    
                return True, channel_id
        except Exception:
            return False, None

    def is_running(self) -> bool:
        return self.progress.status == "running"
