from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from database.models import Base


class TVLibrary(Base):
    """A collection/library for TV series linked to a Telegram channel."""
    __tablename__ = 'tv_libraries'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    name_en = Column(String, nullable=True)
    slug = Column(String, nullable=False, unique=True)
    telegram_channel = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    telegram_channel_id = Column(String)
    display_order = Column(Integer, default=0, nullable=True)

    series = relationship("TVSeries", back_populates="library", cascade="all, delete-orphan")


class TMDBTVSeries(Base):
    """TMDB metadata for a TV series."""
    __tablename__ = 'tmdb_tv_series'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer, nullable=False, unique=True)
    name = Column(String)
    original_name = Column(String)
    overview = Column(Text)
    poster_path = Column(String)
    backdrop_path = Column(String)
    first_air_date = Column(String)
    vote_average = Column(Float)
    number_of_seasons = Column(Integer)
    number_of_episodes = Column(Integer)
    genres = Column(String)  # Stored as JSON string
    status = Column(String)  # e.g. "Returning Series", "Ended"


class TVSeries(Base):
    """A TV series scraped from a Telegram channel."""
    __tablename__ = 'tv_series'

    id = Column(Integer, primary_key=True, autoincrement=True)
    library_id = Column(Integer, ForeignKey('tv_libraries.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    telegram_channel_link = Column(String)  # The invite/channel link found inside the message
    tmdb_tv_id = Column(Integer, ForeignKey('tmdb_tv_series.id'))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('title', 'library_id', name='uix_tv_series_title_library'),
    )

    library = relationship("TVLibrary", back_populates="series")
    tmdb_tv = relationship("TMDBTVSeries")


class FeaturedTVSeries(Base):
    """Manually managed Trending/Popular/Currently Airing TV series independent of scraped libraries."""
    __tablename__ = 'featured_tv_series'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    poster_url = Column(String, nullable=False)
    telegram_channel_link = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True, default="Trending")  # e.g. "Trending", "Popular", "Currently Airing"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
