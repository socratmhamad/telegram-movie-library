from __future__ import annotations

import os
from pathlib import Path
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean, DateTime, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Library(Base):
    __tablename__ = 'libraries'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True)
    telegram_channel = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean)
    last_scan = Column(DateTime)
    last_migration = Column(DateTime)
    telegram_channel_id = Column(String)

    movies = relationship("Movie", back_populates="library")


class TMDBMovie(Base):
    __tablename__ = 'tmdb_movies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer, nullable=False, unique=True)
    title = Column(String)
    original_title = Column(String)
    overview = Column(Text)
    poster_path = Column(String)
    backdrop_path = Column(String)
    release_date = Column(String)
    vote_average = Column(Float)
    runtime = Column(Integer)
    genres = Column(String)  # Stored as JSON string
    imdb_id = Column(String)

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    library_id = Column(Integer, ForeignKey('libraries.id'), nullable=False)
    title = Column(String, nullable=False)
    tmdb_movie_id = Column(Integer, ForeignKey('tmdb_movies.id'))

    __table_args__ = (
        UniqueConstraint('tmdb_movie_id', 'library_id', name='uix_movie_tmdb_library'),
    )

    library = relationship("Library", back_populates="movies")
    tmdb_movie = relationship("TMDBMovie")
    telegram_messages = relationship("TelegramMessage", back_populates="movie", cascade="all, delete-orphan")

class TelegramMessage(Base):
    __tablename__ = 'telegram_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete="CASCADE"), nullable=False)
    message_id = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('movie_id', 'message_id', name='uix_message_movie'),
    )

    movie = relationship("Movie", back_populates="telegram_messages")


def get_db_url(url: str | None = None, fallback_path: Path | None = None) -> str:
    """Helper to determine the database URL"""
    if url:
        # SQLAlchemy requires postgresql:// instead of postgres://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        print(f"[DB] Using PostgreSQL: {url.split('@')[-1] if '@' in url else '(configured)'}")
        return url

    # Default to sqlite
    if fallback_path:
        db_path = f"sqlite:///{fallback_path.absolute()}"
    else:
        db_path = "sqlite:///database/movies.db"
    print(f"[DB] Using SQLite: {db_path}")
    return db_path


def init_db(url: str):
    """Initializes the database and returns the sessionmaker."""
    # SQLAlchemy requires postgresql:// instead of postgres://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
