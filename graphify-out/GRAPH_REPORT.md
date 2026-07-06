# Graph Report - Movis_with_Telegram  (2026-07-06)

## Corpus Check
- 54 files · ~13,887 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 313 nodes · 605 edges · 27 communities (20 shown, 7 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fefb1172`
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
- [[_COMMUNITY_main.py|main.py]]
- [[_COMMUNITY_MovieGrid.jsx|MovieGrid.jsx]]
- [[_COMMUNITY_TelegramClient|TelegramClient]]
- [[_COMMUNITY_Any|Any]]
- [[_COMMUNITY_Session|Session]]
- [[_COMMUNITY_Path|Path]]

## God Nodes (most connected - your core abstractions)
1. `MovieQueries` - 35 edges
2. `MovieDatabase` - 17 edges
3. `process_movie()` - 15 edges
4. `get_db_url()` - 12 edges
5. `Movie` - 11 edges
6. `request()` - 10 edges
7. `TaskProgress` - 9 edges
8. `BaseTelegramTask` - 9 edges
9. `TelegramMessage` - 9 edges
10. `parse_movie_message()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `create_library()` --indirect_call--> `Library`  [INFERRED]
  backend/routers/libraries.py → database/models.py
- `main()` --indirect_call--> `TMDBMovie`  [INFERRED]
  migrate_tmdb_arabic.py → database/models.py
- `main()` --indirect_call--> `TMDBMovie`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --indirect_call--> `Movie`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --indirect_call--> `TelegramMessage`  [INFERRED]
  migrate_to_postgres.py → database/models.py

## Import Cycles
- None detected.

## Communities (27 total, 7 thin omitted)

### Community 0 - "client.js"
Cohesion: 0.10
Nodes (35): createLibrary(), fetchFeatured(), fetchGenres(), fetchLibraries(), fetchLibrary(), fetchMovie(), fetchMovies(), fetchStats() (+27 more)

### Community 1 - "library_import.py"
Cohesion: 0.10
Nodes (22): get_database_url(), Get the database URL from the environment for SQLAlchemy., BaseTelegramTask, Any, Tests if the provided channel is accessible and returns its numeric ID., TaskProgress, LibraryImportService, Starts a background migration task to update links for existing movies. (+14 more)

### Community 2 - "MovieQueries"
Cohesion: 0.07
Nodes (33): Any, MovieQueries, Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy., Return top-rated movies with backdrop images across all libraries.          Used, create_library(), get_library(), _get_queries(), LibraryCreateRequest (+25 more)

### Community 3 - "MovieDatabase"
Cohesion: 0.67
Nodes (3): get_database_path(), Path, Resolve the database path from the environment.      Keeps the backend independe

### Community 4 - "parse_movie_message"
Cohesion: 0.14
Nodes (15): Message, _clean_title(), extract_movie_title(), _extract_quality(), _is_valid_title(), parse_movie_message(), ParsedMovie, Extract a likely movie title and supported video quality from a Telegram message (+7 more)

### Community 5 - "movies.py"
Cohesion: 0.12
Nodes (23): FeaturedMovieItem, FeaturedResponse, GenreListResponse, MovieDetailResponse, MovieListItem, PaginatedResponse, _parse_genres(), Any (+15 more)

### Community 7 - "process_movie"
Cohesion: 0.21
Nodes (10): Lock, clean_title_and_extract_year(), main(), process_movie(), Any, Return a console-safe version of *text* (handles Windows cp1252)., Clean movie titles before searching TMDB and extract release year if available., _safe() (+2 more)

### Community 8 - "package.json"
Cohesion: 0.12
Nodes (16): dependencies, framer-motion, react, react-dom, react-router-dom, devDependencies, vite, @vitejs/plugin-react (+8 more)

### Community 9 - "tmdb_service.py"
Cohesion: 0.16
Nodes (19): init_db(), Initializes the database and returns the sessionmaker., fetch_arabic_metadata(), load_state(), main(), Load the set of already processed TMDB IDs., Save the set of processed TMDB IDs atomically., Fetch TMDB metadata preferring Arabic.     Falls back to English if the Arabic t (+11 more)

### Community 10 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 21 - "main.py"
Cohesion: 0.16
Nodes (10): _path_env(), Settings, Return a console-safe version of *text* (handles Windows cp1252)., run(), _safe(), migrate(), Path, get_telegram_client() (+2 more)

### Community 22 - "MovieGrid.jsx"
Cohesion: 0.40
Nodes (4): MovieCard(), cardVariants, gridVariants, MovieGrid()

## Knowledge Gaps
- **23 isolated node(s):** `Settings`, `name`, `private`, `version`, `type` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MovieQueries` connect `MovieQueries` to `movies.py`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `get_db_url()` connect `library_import.py` to `tmdb_service.py`, `MovieQueries`, `main.py`, `process_movie`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `MovieDatabase` connect `library_import.py` to `tmdb_service.py`, `process_movie`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `MovieQueries` (e.g. with `LibraryCreateRequest` and `LibraryUpdateRequest`) actually correct?**
  _`MovieQueries` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Settings`, `Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy.`, `Return top-rated movies with backdrop images across all libraries.          Used` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `client.js` be split into smaller, more focused modules?**
  _Cohesion score 0.1027450980392157 - nodes in this community are weakly interconnected._
- **Should `library_import.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10453283996299723 - nodes in this community are weakly interconnected._