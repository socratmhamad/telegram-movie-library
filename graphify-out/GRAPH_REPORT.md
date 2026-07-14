# Graph Report - Movis_with_Telegram  (2026-07-14)

## Corpus Check
- 62 files · ~26,294 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 241 nodes · 445 edges · 19 communities (15 shown, 4 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `81948433`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_MovieQueries|MovieQueries]]
- [[_COMMUNITY_movies.py|movies.py]]
- [[_COMMUNITY_App.jsx|App.jsx]]
- [[_COMMUNITY_process_movie|process_movie]]
- [[_COMMUNITY_package.json|package.json]]
- [[_COMMUNITY_get_db_url|get_db_url]]
- [[_COMMUNITY_tmdb_service.py|tmdb_service.py]]
- [[_COMMUNITY_.oxlintrc.json|.oxlintrc.json]]
- [[_COMMUNITY_run.py|run.py]]
- [[_COMMUNITY_config.py|config.py]]
- [[_COMMUNITY__parse_genres|_parse_genres]]
- [[_COMMUNITY_Any|Any]]
- [[_COMMUNITY_Path|Path]]
- [[_COMMUNITY___init__.py|__init__.py]]

## God Nodes (most connected - your core abstractions)
1. `MovieQueries` - 23 edges
2. `Movie` - 16 edges
3. `process_movie()` - 15 edges
4. `TelegramMessage` - 13 edges
5. `MovieDatabase` - 12 edges
6. `Library` - 12 edges
7. `TMDBMovie` - 12 edges
8. `get_db_url()` - 12 edges
9. `migrate()` - 11 edges
10. `run_test()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `MovieQueries` --uses--> `Library`  [INFERRED]
  backend/database.py → database/models.py
- `MovieQueries` --uses--> `Movie`  [INFERRED]
  backend/database.py → database/models.py
- `MovieQueries` --uses--> `TelegramMessage`  [INFERRED]
  backend/database.py → database/models.py
- `MovieQueries` --uses--> `TMDBMovie`  [INFERRED]
  backend/database.py → database/models.py
- `MatchResult` --uses--> `Library`  [INFERRED]
  migrate_channel_links.py → database/models.py

## Import Cycles
- None detected.

## Communities (19 total, 4 thin omitted)

### Community 0 - "MovieQueries"
Cohesion: 0.15
Nodes (26): Any, Base, init_db(), Library, Movie, Initializes the database and returns the sessionmaker., TelegramMessage, TMDBMovie (+18 more)

### Community 1 - "movies.py"
Cohesion: 0.08
Nodes (34): Health-check / welcome endpoint., root(), get_database_path(), get_database_url(), get_telegram_channel_id(), Path, Resolve the database path from the environment.      Keeps the backend indepen, Get the database URL from the environment for SQLAlchemy. (+26 more)

### Community 2 - "App.jsx"
Cohesion: 0.13
Nodes (18): plugins, fetchGenres(), fetchMovie(), fetchMovies(), fetchStats(), request(), App(), GenreFilter() (+10 more)

### Community 3 - "process_movie"
Cohesion: 0.14
Nodes (17): get_db_url(), Helper to determine the database URL, Lock, Return a console-safe version of *text* (handles Windows cp1252)., run(), _safe(), MovieDatabase, Path (+9 more)

### Community 4 - "package.json"
Cohesion: 0.11
Nodes (18): dependencies, react, react-dom, devDependencies, vite, @vitejs/plugin-react, name, private (+10 more)

### Community 5 - "get_db_url"
Cohesion: 0.15
Nodes (7): _path_env(), Path, Settings, fix_message_id_constraint.py — One-time schema migration.  Removes the old UNIQU, get_telegram_client(), TelegramClient, Create, authenticate, and cleanly disconnect a Telethon client.

### Community 6 - "tmdb_service.py"
Cohesion: 0.36
Nodes (10): main(), build_poster_url(), _choose_best_match(), get_movie_details(), _normalize_title(), Any, Search TMDB by movie title and return the best matching result.      Returned, Fetch detailed TMDB metadata for a movie.      Returned keys:     - poster_pa (+2 more)

### Community 7 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): rules, react/only-export-components, react/rules-of-hooks, $schema, warn

### Community 14 - "config.py"
Cohesion: 0.14
Nodes (15): Message, _clean_title(), extract_movie_title(), _extract_quality(), _is_valid_title(), parse_movie_message(), ParsedMovie, Extract a likely movie title and supported video quality from a Telegram message (+7 more)

### Community 15 - "_parse_genres"
Cohesion: 0.24
Nodes (4): MovieDatabase, SQLAlchemy repository for storing scraped Telegram movie records., Return the set of all Telegram message IDs already stored., Session

## Knowledge Gaps
- **16 isolated node(s):** `Settings`, `$schema`, `oxc`, `react/rules-of-hooks`, `warn` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MovieQueries` connect `movies.py` to `MovieQueries`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `get_db_url()` connect `process_movie` to `MovieQueries`, `movies.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MovieQueries` (e.g. with `Library` and `Movie`) actually correct?**
  _`MovieQueries` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Movie` (e.g. with `MovieQueries` and `.get_genres()`) actually correct?**
  _`Movie` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `TelegramMessage` (e.g. with `MovieQueries` and `.get_movie()`) actually correct?**
  _`TelegramMessage` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Telegram movie scraper package.`, `SQLAlchemy repository for storing scraped Telegram movie records.`, `Return the set of all Telegram message IDs already stored.` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MovieQueries` be split into smaller, more focused modules?**
  _Cohesion score 0.14935988620199148 - nodes in this community are weakly interconnected._