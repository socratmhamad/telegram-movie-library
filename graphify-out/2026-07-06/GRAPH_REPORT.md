# Graph Report - .  (2026-07-05)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 280 nodes · 585 edges · 19 communities (17 shown, 2 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 31 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ca509529`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_client.js|client.js]]
- [[_COMMUNITY_library_import.py|library_import.py]]
- [[_COMMUNITY_MovieQueries|MovieQueries]]
- [[_COMMUNITY_MovieDatabase|MovieDatabase]]
- [[_COMMUNITY_parse_movie_message|parse_movie_message]]
- [[_COMMUNITY_movies.py|movies.py]]
- [[_COMMUNITY_telegram.py|telegram.py]]
- [[_COMMUNITY_process_movie|process_movie]]
- [[_COMMUNITY_package.json|package.json]]
- [[_COMMUNITY_tmdb_service.py|tmdb_service.py]]
- [[_COMMUNITY_.oxlintrc.json|.oxlintrc.json]]
- [[_COMMUNITY_run.py|run.py]]
- [[_COMMUNITY___init__.py|__init__.py]]

## God Nodes (most connected - your core abstractions)
1. `MovieQueries` - 33 edges
2. `MovieDatabase` - 19 edges
3. `Movie` - 16 edges
4. `process_movie()` - 15 edges
5. `Library` - 13 edges
6. `parse_movie_message()` - 13 edges
7. `get_db_url()` - 12 edges
8. `get_telegram_client()` - 11 edges
9. `TelegramMessage` - 10 edges
10. `TMDBClient` - 10 edges

## Surprising Connections (you probably didn't know these)
- `LibraryImportService` --uses--> `TMDBClient`  [INFERRED]
  backend/services/library_import.py → update_tmdb.py
- `create_library()` --indirect_call--> `Library`  [INFERRED]
  backend/routers/libraries.py → database/models.py
- `main()` --indirect_call--> `TMDBMovie`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --indirect_call--> `Movie`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --indirect_call--> `TelegramMessage`  [INFERRED]
  migrate_to_postgres.py → database/models.py

## Import Cycles
- None detected.

## Communities (19 total, 2 thin omitted)

### Community 0 - "client.js"
Cohesion: 0.10
Nodes (31): createLibrary(), fetchGenres(), fetchLibraries(), fetchLibrary(), fetchMovie(), fetchMovies(), fetchStats(), fetchTelegramConfig() (+23 more)

### Community 1 - "library_import.py"
Cohesion: 0.12
Nodes (18): get_database_path(), get_database_url(), Path, Resolve the database path from the environment.      Keeps the backend independe, Get the database URL from the environment for SQLAlchemy., BaseTelegramTask, Any, Tests if the provided channel is accessible and returns its numeric ID. (+10 more)

### Community 2 - "MovieQueries"
Cohesion: 0.14
Nodes (19): MovieQueries, Any, Session, Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy., StatsResponse, create_library(), get_library(), _get_queries() (+11 more)

### Community 3 - "MovieDatabase"
Cohesion: 0.16
Nodes (13): get_telegram_channel_id(), Return the numeric Telegram channel ID (without the ``-100`` prefix).      Used, Base, init_db(), Movie, Initializes the database and returns the sessionmaker., TelegramMessage, TMDBMovie (+5 more)

### Community 4 - "parse_movie_message"
Cohesion: 0.13
Nodes (18): Return a console-safe version of *text* (handles Windows cp1252)., run(), _safe(), Message, _clean_title(), extract_movie_title(), _extract_quality(), _is_valid_title() (+10 more)

### Community 5 - "movies.py"
Cohesion: 0.13
Nodes (19): GenreListResponse, MovieDetailResponse, MovieListItem, PaginatedResponse, _parse_genres(), Any, Accept a JSON string or a plain list and always return ``list[str]``., TelegramMessageResponse (+11 more)

### Community 6 - "telegram.py"
Cohesion: 0.10
Nodes (17): get_config(), _get_library(), _get_queries(), get_task_status(), import_library(), Request, Returns the current telegram channel for this library., Tests connection to the specified Telegram channel and saves its numeric ID. (+9 more)

### Community 7 - "process_movie"
Cohesion: 0.21
Nodes (10): Lock, clean_title_and_extract_year(), main(), process_movie(), Any, Return a console-safe version of *text* (handles Windows cp1252)., Clean movie titles before searching TMDB and extract release year if available., _safe() (+2 more)

### Community 8 - "package.json"
Cohesion: 0.12
Nodes (15): dependencies, react, react-dom, react-router-dom, devDependencies, vite, @vitejs/plugin-react, name (+7 more)

### Community 9 - "tmdb_service.py"
Cohesion: 0.36
Nodes (10): main(), build_poster_url(), _choose_best_match(), get_movie_details(), _normalize_title(), Any, Search TMDB by movie title and return the best matching result.      Returned ke, Fetch detailed TMDB metadata for a movie.      Returned keys:     - poster_path (+2 more)

### Community 10 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

## Knowledge Gaps
- **17 isolated node(s):** `Settings`, `$schema`, `plugins`, `react/rules-of-hooks`, `react/only-export-components` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MovieQueries` connect `MovieQueries` to `library_import.py`, `MovieDatabase`, `movies.py`, `telegram.py`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `MovieDatabase` connect `MovieDatabase` to `library_import.py`, `parse_movie_message`, `process_movie`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `get_db_url()` connect `library_import.py` to `MovieDatabase`, `parse_movie_message`, `process_movie`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `MovieQueries` (e.g. with `LibraryCreateRequest` and `LibraryUpdateRequest`) actually correct?**
  _`MovieQueries` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Movie` (e.g. with `.get_genres()` and `.get_movie()`) actually correct?**
  _`Movie` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Library` (e.g. with `.get_libraries()` and `.get_library_by_slug()`) actually correct?**
  _`Library` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Resolve the database path from the environment.      Keeps the backend independe`, `Get the database URL from the environment for SQLAlchemy.`, `Return the numeric Telegram channel ID (without the ``-100`` prefix).      Used` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._