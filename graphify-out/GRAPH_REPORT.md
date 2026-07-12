# Graph Report - .  (2026-07-12)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 172 nodes · 296 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ca509529`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MovieQueries
- movies.py
- App.jsx
- process_movie
- package.json
- get_db_url
- tmdb_service.py
- .oxlintrc.json
- run.py

## God Nodes (most connected - your core abstractions)
1. `MovieQueries` - 17 edges
2. `process_movie()` - 15 edges
3. `get_db_url()` - 8 edges
4. `Stats` - 8 edges
5. `Movie` - 7 edges
6. `search_movie()` - 7 edges
7. `TMDBClient` - 7 edges
8. `main()` - 7 edges
9. `TMDBMovie` - 6 edges
10. `TelegramMessage` - 6 edges

## Surprising Connections (you probably didn't know these)
- `main()` --indirect_call--> `TMDBMovie`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --indirect_call--> `Movie`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --indirect_call--> `TelegramMessage`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --calls--> `get_db_url()`  [EXTRACTED]
  update_tmdb.py → database/models.py
- `run()` --calls--> `get_db_url()`  [EXTRACTED]
  main.py → database/models.py

## Import Cycles
- None detected.

## Communities (14 total, 1 thin omitted)

### Community 0 - "MovieQueries"
Cohesion: 0.13
Nodes (20): Health-check / welcome endpoint., root(), get_database_path(), get_database_url(), get_telegram_channel_id(), Path, Resolve the database path from the environment.      Keeps the backend indepen, Get the database URL from the environment for SQLAlchemy. (+12 more)

### Community 1 - "movies.py"
Cohesion: 0.11
Nodes (23): GenreListResponse, MovieDetailResponse, MovieListItem, PaginatedResponse, _parse_genres(), Any, Accept a JSON string or a plain list and always return ``list[str]``., StatsResponse (+15 more)

### Community 2 - "App.jsx"
Cohesion: 0.15
Nodes (16): fetchGenres(), fetchMovie(), fetchMovies(), fetchStats(), request(), App(), GenreFilter(), Layout() (+8 more)

### Community 3 - "process_movie"
Cohesion: 0.20
Nodes (11): Lock, MovieDatabase, clean_title_and_extract_year(), main(), process_movie(), Any, Return a console-safe version of *text* (handles Windows cp1252)., Clean movie titles before searching TMDB and extract release year if available. (+3 more)

### Community 4 - "package.json"
Cohesion: 0.11
Nodes (18): dependencies, react, react-dom, devDependencies, vite, @vitejs/plugin-react, name, private (+10 more)

### Community 5 - "get_db_url"
Cohesion: 0.18
Nodes (9): _path_env(), Path, Settings, get_db_url(), Path, Helper to determine the database URL, Return a console-safe version of *text* (handles Windows cp1252)., run() (+1 more)

### Community 6 - "tmdb_service.py"
Cohesion: 0.36
Nodes (10): main(), build_poster_url(), _choose_best_match(), get_movie_details(), _normalize_title(), Any, Search TMDB by movie title and return the best matching result.      Returned, Fetch detailed TMDB metadata for a movie.      Returned keys:     - poster_pa (+2 more)

### Community 7 - ".oxlintrc.json"
Cohesion: 0.25
Nodes (7): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, warn

## Knowledge Gaps
- **16 isolated node(s):** `Settings`, `$schema`, `oxc`, `react/rules-of-hooks`, `warn` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_db_url()` connect `get_db_url` to `MovieQueries`, `process_movie`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `MovieQueries` connect `MovieQueries` to `movies.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **What connects `Settings`, `$schema`, `oxc` to the rest of the system?**
  _16 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MovieQueries` be split into smaller, more focused modules?**
  _Cohesion score 0.13118279569892474 - nodes in this community are weakly interconnected._
- **Should `movies.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10804597701149425 - nodes in this community are weakly interconnected._
- **Should `App.jsx` be split into smaller, more focused modules?**
  _Cohesion score 0.1455026455026455 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._