from __future__ import annotations

from contextlib import contextmanager
import json
from typing import Iterator, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.models import init_db, Movie, TMDBMovie, TelegramMessage, MovieAlias

class MovieDatabase:
    """SQLAlchemy repository for storing scraped Telegram movie records."""

    def __init__(self, database_url: str) -> None:
        self.SessionLocal = init_db(database_url)

    @contextmanager
    def _connection(self) -> Iterator[Session]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_known_message_ids(self, library_id: int) -> set[int]:
        """Return the set of all Telegram message IDs already stored for the library."""
        with self._connection() as session:
            rows = session.execute(
                select(TelegramMessage.message_id)
                .join(Movie, TelegramMessage.movie_id == Movie.id)
                .where(Movie.library_id == library_id)
            ).scalars().all()
            return set(rows)

    def get_or_create_movie(self, title: str, library_id: int) -> int:
        with self._connection() as session:
            return self._get_or_create_movie(session, title, library_id)

    def save_telegram_message(self, movie_id: int, message_id: int) -> bool:
        with self._connection() as session:
            return self._save_telegram_message(session, movie_id, message_id)

    def save_movie_message(self, title: str, message_id: int, library_id: int) -> bool:
        with self._connection() as session:
            movie_id = self._get_or_create_movie(session, title, library_id)
            return self._save_telegram_message(session, movie_id, message_id)

    def save_movies(self, movies: Iterable[dict[str, object]], library_id: int) -> int:
        saved_count = 0
        with self._connection() as session:
            for movie_dict in movies:
                title = str(movie_dict["title"])
                message_id = int(str(movie_dict["message_id"]))
                
                movie_id = self._get_or_create_movie(session, title, library_id)
                inserted = self._save_telegram_message(session, movie_id, message_id)
                if inserted:
                    saved_count += 1
        return saved_count

    def get_movies_without_tmdb(self, library_id: int | None = None) -> list[dict[str, object]]:
        with self._connection() as session:
            query = select(Movie.id, Movie.title).where(Movie.tmdb_movie_id.is_(None))
            if library_id is not None:
                query = query.where(Movie.library_id == library_id)
            query = query.order_by(Movie.title)
            
            rows = session.execute(query).all()
            # Return dicts to emulate sqlite3.Row for legacy compat in update_tmdb.py
            return [{"id": row.id, "title": row.title} for row in rows]

    def save_tmdb_movie(self, tmdb_movie: dict[str, object]) -> int:
        with self._connection() as session:
            return self._save_tmdb_movie(session, tmdb_movie)

    def link_movie_to_tmdb(self, movie_id: int, tmdb_movie_id: int) -> None:
        with self._connection() as session:
            movie = session.execute(select(Movie).where(Movie.id == movie_id)).scalar_one_or_none()
            if not movie:
                return
                
            from sqlalchemy import update
            
            # Check if another movie in the same library already has this tmdb_id
            existing = session.execute(
                select(Movie)
                .where(Movie.tmdb_movie_id == tmdb_movie_id, Movie.library_id == movie.library_id, Movie.id != movie_id)
            ).scalar_one_or_none()
            
            if existing:
                # Merge current movie into existing
                session.execute(
                    update(MovieAlias).where(MovieAlias.movie_id == movie_id).values(movie_id=existing.id)
                )
                session.execute(
                    update(TelegramMessage).where(TelegramMessage.movie_id == movie_id).values(movie_id=existing.id)
                )
                session.delete(movie)
            else:
                movie.tmdb_movie_id = tmdb_movie_id

    def _get_or_create_movie(self, session: Session, title: str, library_id: int) -> int:
        alias = session.execute(
            select(MovieAlias).where(MovieAlias.title == title, MovieAlias.library_id == library_id)
        ).scalar_one_or_none()
        
        if alias is not None:
            return alias.movie_id
            
        movie = Movie(title=title, library_id=library_id)
        session.add(movie)
        try:
            session.flush()
            new_alias = MovieAlias(title=title, library_id=library_id, movie_id=movie.id)
            session.add(new_alias)
            session.flush()
            return movie.id
        except IntegrityError:
            session.rollback()
            alias = session.execute(
                select(MovieAlias).where(MovieAlias.title == title, MovieAlias.library_id == library_id)
            ).scalar_one()
            return alias.movie_id

    def _save_telegram_message(
        self,
        session: Session,
        movie_id: int,
        message_id: int,
    ) -> bool:
        exists = session.execute(
            select(TelegramMessage).where(TelegramMessage.message_id == message_id)
        ).scalar_one_or_none()
        
        if exists is not None:
            return False
            
        msg = TelegramMessage(movie_id=movie_id, message_id=message_id)
        session.add(msg)
        try:
            session.flush()
            return True
        except IntegrityError:
            session.rollback()
            return False

    def _save_tmdb_movie(
        self,
        session: Session,
        tmdb_movie: dict[str, object],
    ) -> int:
        tmdb_id = int(str(tmdb_movie["tmdb_id"]))
        movie = session.execute(
            select(TMDBMovie).where(TMDBMovie.tmdb_id == tmdb_id)
        ).scalar_one_or_none()
        
        if movie is None:
            genres = tmdb_movie.get("genres")
            genres_value = json.dumps(genres if isinstance(genres, list) else [])
            
            movie = TMDBMovie(
                tmdb_id=tmdb_id,
                title=tmdb_movie.get("title"),
                original_title=tmdb_movie.get("original_title"),
                overview=tmdb_movie.get("overview"),
                poster_path=tmdb_movie.get("poster_path"),
                backdrop_path=tmdb_movie.get("backdrop_path"),
                release_date=tmdb_movie.get("release_date"),
                vote_average=tmdb_movie.get("vote_average"),
                runtime=tmdb_movie.get("runtime"),
                genres=genres_value,
                imdb_id=tmdb_movie.get("imdb_id"),
            )
            session.add(movie)
            try:
                session.flush()
            except IntegrityError:
                session.rollback()
                movie = session.execute(
                    select(TMDBMovie).where(TMDBMovie.tmdb_id == tmdb_id)
                ).scalar_one()

        return int(str(movie.id))
