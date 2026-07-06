import asyncio
import time
from sqlalchemy import select
from config import settings

from backend.services.base_task import BaseTelegramTask, TaskProgress
from scraper.telegram_client import get_telegram_client
from scraper.parser import parse_movie_message
from scraper.database import MovieDatabase
from database.models import Library
from update_tmdb import TMDBClient, clean_title_and_extract_year, _choose_best_match
from backend.config import get_database_url, get_database_path
from database.models import get_db_url
from datetime import datetime, timezone

class LibraryImportService(BaseTelegramTask):
    def start_import(self, library_id: int, target_channel: str, background_tasks=None):
        if self.is_running():
            raise ValueError("An import task is already running.")

        self.progress = TaskProgress(
            status="running",
            mode="import",
            target_channel=target_channel,
            start_time=time.time()
        )
        
        if background_tasks:
            background_tasks.add_task(self._run_import, library_id, target_channel)
        else:
            loop = asyncio.get_running_loop()
            self._current_task = loop.create_task(self._run_import(library_id, target_channel))

    async def _run_import(self, library_id: int, target_channel: str):
        try:
            db_url = get_db_url(get_database_url(), get_database_path())
            movie_db = MovieDatabase(db_url)
            known_ids = movie_db.get_known_message_ids(library_id)
            
            tmdb_client = TMDBClient(settings.tmdb_api_key) if settings.tmdb_api_key else None
            
            async with get_telegram_client() as client:
                async for message in client.iter_messages(target_channel, limit=None):
                    self.progress.total_scanned += 1
                    
                    if message.id in known_ids:
                        continue
                        
                    parsed_movie = parse_movie_message(message.message)
                    if not parsed_movie:
                        continue
                        
                    self.progress.matched_movies += 1 # we successfully parsed one
                    
                    # Create or get movie and save message
                    title = parsed_movie.title
                    
                    # Save movie and message
                    with self.SessionLocal() as session:
                        movie_id = movie_db._get_or_create_movie(session, title, library_id)
                        inserted = movie_db._save_telegram_message(session, movie_id, message.id)
                        session.commit()
                        
                        if inserted:
                            self.progress.new_movies_added += 1
                            self.progress.updated_links += 1 # consider it a link made
                            
                            # Do TMDB lookup if enabled and new movie
                            if tmdb_client:
                                clean_title, year = clean_title_and_extract_year(title)
                                search_result = await asyncio.to_thread(tmdb_client.search_movie, clean_title, year)
                                if search_result and search_result.get("tmdb_id"):
                                    details = await asyncio.to_thread(tmdb_client.get_movie_details, search_result["tmdb_id"])
                                    if details:
                                        search_result.update(details)
                                        # Now save tmdb movie
                                        tmdb_movie_id = movie_db._save_tmdb_movie(session, search_result)
                                        
                                        # link movie to tmdb
                                        from database.models import Movie
                                        movie = session.execute(select(Movie).where(Movie.id == movie_id)).scalar_one_or_none()
                                        if movie:
                                            movie.tmdb_movie_id = tmdb_movie_id
                                            
                                        session.commit()
                                        self.progress.tmdb_lookups_completed += 1

            self.progress.status = "completed"
            
            with self.SessionLocal() as session:
                lib = session.execute(select(Library).where(Library.id == library_id)).scalar_one_or_none()
                if lib:
                    lib.last_scan = datetime.now(timezone.utc)
                    session.commit()
                    
        except Exception as e:
            self.progress.status = "error"
            self.progress.error_message = str(e)
        finally:
            self.progress.end_time = time.time()
            self._current_task = None

library_import_service = LibraryImportService()
