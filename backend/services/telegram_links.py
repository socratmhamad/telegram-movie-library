import asyncio
import time
from typing import Dict, Any, List

from sqlalchemy import select, delete

from backend.services.base_task import BaseTelegramTask, TaskProgress
from database.models import Movie, TelegramMessage, Library
from scraper.telegram_client import get_telegram_client
from scraper.parser import parse_movie_message
from datetime import datetime, timezone

class TelegramLinkService(BaseTelegramTask):
    def start_update(self, library_id: int, target_channel: str, background_tasks = None):
        """Starts a background migration task to update links for existing movies."""
        if self.is_running():
            raise ValueError("An update task is already running.")

        self.progress = TaskProgress(
            status="running",
            mode="update_links",
            target_channel=target_channel,
            start_time=time.time()
        )
        
        if background_tasks:
            background_tasks.add_task(self._run_update, library_id, target_channel)
        else:
            loop = asyncio.get_running_loop()
            self._current_task = loop.create_task(self._run_update(library_id, target_channel))

    async def _run_update(self, library_id: int, target_channel: str):
        try:
            with self.SessionLocal() as session:
                # Get all known movie titles to avoid querying repeatedly
                known_movies = {
                    row.title: row.id 
                    for row in session.execute(
                        select(Movie.title, Movie.id)
                        .where(Movie.library_id == library_id)
                    ).all()
                }

                # Wipe the current telegram_messages for THIS library
                session.execute(
                    delete(TelegramMessage)
                    .where(TelegramMessage.movie_id.in_(
                        select(Movie.id).where(Movie.library_id == library_id)
                    ))
                )
                session.commit()

                async with get_telegram_client() as client:
                    async for message in client.iter_messages(target_channel, limit=None):
                        self.progress.total_scanned += 1
                        
                        parsed_movie = parse_movie_message(message.message)
                        if not parsed_movie:
                            continue
                            
                        title = parsed_movie.title
                        movie_id = known_movies.get(title)

                        if movie_id is not None:
                            self.progress.matched_movies += 1
                            try:
                                msg = TelegramMessage(movie_id=movie_id, message_id=message.id)
                                session.add(msg)
                                session.commit()
                                self.progress.updated_links += 1
                            except Exception:
                                session.rollback()
                                self.progress.failed_updates += 1
                        else:
                            # Missing movie - in channel but not in our DB
                            self.progress.missing_movies.append({
                                "title": title,
                                "message_id": message.id,
                                "quality": parsed_movie.quality
                            })
                            
            self.progress.status = "completed"
            
            with self.SessionLocal() as session:
                lib = session.execute(select(Library).where(Library.id == library_id)).scalar_one_or_none()
                if lib:
                    lib.last_migration = datetime.now(timezone.utc)
                    session.commit()
                        
        except Exception as e:
            self.progress.status = "error"
            self.progress.error_message = str(e)
        finally:
            self.progress.end_time = time.time()
            self._current_task = None

telegram_link_service = TelegramLinkService()
