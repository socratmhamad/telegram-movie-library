# Telegram Movies

A small, modular Telegram movie indexing foundation built with Python, Telethon, and SQLite.

This first step logs in to Telegram, reads messages from a configured channel, extracts likely movie titles, and stores movie titles separately from Telegram message availability in `database/movies.db`.

## Project Structure

```text
telegram-movies/
|-- scraper/
|   |-- __init__.py
|   |-- telegram_client.py
|   |-- scraper.py
|   |-- parser.py
|   `-- database.py
|-- database/
|   `-- movies.db
|-- config.py
|-- tmdb_service.py
|-- test_tmdb.py
|-- update_tmdb.py
|-- requirements.txt
|-- main.py
|-- .env.example
|-- .gitignore
`-- README.md
```

`database/movies.db` is created automatically the first time the scraper runs.

## File Purposes

- `scraper/__init__.py`: Marks `scraper` as a Python package.
- `scraper/telegram_client.py`: Creates and authenticates the Telethon client.
- `scraper/scraper.py`: Reads Telegram channel messages and converts valid posts into movie records.
- `scraper/parser.py`: Extracts a likely movie title and supported quality from raw Telegram message text.
- `scraper/database.py`: Creates the SQLite schema, keeps movie titles unique, and saves Telegram message records for each movie.
- `database/.gitkeep`: Keeps the database folder in the project before `movies.db` is generated.
- `config.py`: Loads settings from environment variables or `.env`.
- `tmdb_service.py`: Provides standalone TMDB lookup functions without touching the database.
- `test_tmdb.py`: Verifies TMDB communication from the command line before SQLite integration.
- `update_tmdb.py`: Enriches local movie rows with TMDB metadata and links them to `tmdb_movies`.
- `requirements.txt`: Lists Python dependencies.
- `main.py`: Application entry point that wires configuration, Telegram scraping, and database saving together.
- `.env.example`: Documents the required environment variables.
- `.gitignore`: Keeps secrets, Telegram session files, Python cache files, and local database files out of git.
- `README.md`: Explains setup, usage, and project layout.

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    tmdb_movie_id INTEGER,
    FOREIGN KEY (tmdb_movie_id) REFERENCES tmdb_movies (id)
);

CREATE TABLE IF NOT EXISTS telegram_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tmdb_movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id INTEGER NOT NULL UNIQUE,
    title TEXT,
    original_title TEXT,
    overview TEXT,
    poster_path TEXT,
    backdrop_path TEXT,
    release_date TEXT,
    vote_average REAL,
    runtime INTEGER,
    genres TEXT,
    imdb_id TEXT
);
```

Each movie title appears once in `movies`. Every Telegram message is stored in `telegram_messages` and linked back to its movie with `movie_id`.
TMDB metadata is stored once in `tmdb_movies`, and many local movie rows can point to the same TMDB record through `movies.tmdb_movie_id`.

When scraping:

- If a movie title already exists, a duplicate movie row is not created.
- A new `telegram_messages` row is inserted for each new Telegram `message_id`.
- Re-running the scraper skips Telegram messages that are already stored.

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file from `.env.example`:

```bash
copy .env.example .env
```

4. Fill in your Telegram credentials:

```env
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_CHANNEL=channel_username_or_link
TELEGRAM_SESSION_NAME=telegram_movies
MESSAGE_LIMIT=100
DATABASE_PATH=database/movies.db
TMDB_API_KEY=your_tmdb_api_key_here
```

You can get `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` from <https://my.telegram.org/apps>.

## Run

```bash
python main.py
```

On the first run, Telethon may ask for your phone number, login code, and two-factor password if enabled. After login, it stores a local session file so future runs can reuse the session.

## Test TMDB

After adding `TMDB_API_KEY` to `.env`, run:

```bash
python test_tmdb.py Interstellar
```

The script prints the TMDB ID, title, rating, release date, and poster URL for the best match.

## Update TMDB Metadata

After scraping Telegram movies and setting `TMDB_API_KEY`, run:

```bash
python update_tmdb.py
```

The script searches TMDB for every movie where `movies.tmdb_movie_id` is empty, inserts each TMDB movie only once, links the local movie row, and prints processed, matched, and skipped totals.

## Notes

- Supported qualities are `360p`, `480p`, `720p`, `1080p`, and `2160p`.
- Quality text is removed from the movie title before saving. Quality is currently detected for scraper output only and is not stored in the database schema.
- FastAPI backend, React frontend, and automatic synchronization are intentionally left for future project steps.
