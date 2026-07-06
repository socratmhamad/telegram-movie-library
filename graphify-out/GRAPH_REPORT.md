# Graph Report - Movis_with_Telegram  (2026-07-06)

## Corpus Check
- 54 files · ~13,840 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 312 nodes · 634 edges · 21 communities (18 shown, 3 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1c0c246e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_client.js|client.js]]
- [[_COMMUNITY_library_import.py|library_import.py]]
- [[_COMMUNITY_MovieQueries|MovieQueries]]
- [[_COMMUNITY_MovieDatabase|MovieDatabase]]
- [[_COMMUNITY_parse_movie_message|parse_movie_message]]
- [[_COMMUNITY_movies.py|movies.py]]
- [[_COMMUNITY_process_movie|process_movie]]
- [[_COMMUNITY_package.json|package.json]]
- [[_COMMUNITY_tmdb_service.py|tmdb_service.py]]
- [[_COMMUNITY_.oxlintrc.json|.oxlintrc.json]]
- [[_COMMUNITY_run.py|run.py]]
- [[_COMMUNITY___init__.py|__init__.py]]
- [[_COMMUNITY_Path|Path]]

## God Nodes (most connected - your core abstractions)
1. `MovieQueries` - 35 edges
2. `MovieDatabase` - 19 edges
3. `Movie` - 17 edges
4. `process_movie()` - 15 edges
5. `get_db_url()` - 14 edges
6. `Library` - 13 edges
7. `TMDBMovie` - 11 edges
8. `TelegramMessage` - 11 edges
9. `request()` - 10 edges
10. `TaskProgress` - 9 edges

## Surprising Connections (you probably didn't know these)
- `main()` --indirect_call--> `TMDBMovie`  [INFERRED]
  migrate_tmdb_arabic.py → database/models.py
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

## Communities (21 total, 3 thin omitted)

### Community 0 - "client.js"
Cohesion: 0.09
Nodes (39): createLibrary(), fetchFeatured(), fetchGenres(), fetchLibraries(), fetchLibrary(), fetchMovie(), fetchMovies(), fetchStats() (+31 more)

### Community 1 - "library_import.py"
Cohesion: 0.07
Nodes (28): get_database_path(), get_database_url(), get_telegram_channel_id(), Path, Resolve the database path from the environment.      Keeps the backend independe, Get the database URL from the environment for SQLAlchemy., Return the numeric Telegram channel ID (without the ``-100`` prefix).      Used, get_config() (+20 more)

### Community 2 - "MovieQueries"
Cohesion: 0.15
Nodes (18): MovieQueries, Any, Session, Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy., Return top-rated movies with backdrop images across all libraries.          Used, create_library(), get_library(), _get_queries() (+10 more)

### Community 3 - "MovieDatabase"
Cohesion: 0.18
Nodes (12): Base, init_db(), Movie, MovieAlias, Initializes the database and returns the sessionmaker., TelegramMessage, TMDBMovie, main() (+4 more)

### Community 4 - "parse_movie_message"
Cohesion: 0.09
Nodes (24): _path_env(), Path, Settings, Return a console-safe version of *text* (handles Windows cp1252)., run(), _safe(), Message, _clean_title() (+16 more)

### Community 5 - "movies.py"
Cohesion: 0.09
Nodes (29): FeaturedMovieItem, FeaturedResponse, GenreListResponse, MovieDetailResponse, MovieListItem, PaginatedResponse, _parse_genres(), Any (+21 more)

### Community 7 - "process_movie"
Cohesion: 0.21
Nodes (10): Lock, clean_title_and_extract_year(), main(), process_movie(), Any, Return a console-safe version of *text* (handles Windows cp1252)., Clean movie titles before searching TMDB and extract release year if available., _safe() (+2 more)

### Community 8 - "package.json"
Cohesion: 0.12
Nodes (16): dependencies, framer-motion, react, react-dom, react-router-dom, devDependencies, vite, @vitejs/plugin-react (+8 more)

### Community 9 - "tmdb_service.py"
Cohesion: 0.19
Nodes (17): fetch_arabic_metadata(), load_state(), main(), Load the set of already processed TMDB IDs., Save the set of processed TMDB IDs atomically., Fetch TMDB metadata preferring Arabic.     Falls back to English if the Arabic t, save_state(), main() (+9 more)

### Community 10 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

## Knowledge Gaps
- **23 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MovieQueries` connect `MovieQueries` to `library_import.py`, `MovieDatabase`, `movies.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `get_db_url()` connect `library_import.py` to `tmdb_service.py`, `MovieDatabase`, `parse_movie_message`, `process_movie`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `MovieDatabase` connect `MovieDatabase` to `library_import.py`, `parse_movie_message`, `process_movie`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `MovieQueries` (e.g. with `LibraryCreateRequest` and `LibraryUpdateRequest`) actually correct?**
  _`MovieQueries` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Movie` (e.g. with `.get_featured_movies()` and `.get_genres()`) actually correct?**
  _`Movie` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy.`, `Return top-rated movies with backdrop images across all libraries.          Used`, `Accept a JSON string or a plain list and always return ``list[str]``.` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `client.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08709273182957393 - nodes in this community are weakly interconnected._