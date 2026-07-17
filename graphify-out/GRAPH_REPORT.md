# Graph Report - Movis_with_Telegram  (2026-07-17)

## Corpus Check
- 67 files · ~30,299 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 400 nodes · 682 edges · 31 communities (24 shown, 7 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8f3452c3`
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
- [[_COMMUNITY_TaskManager|TaskManager]]
- [[_COMMUNITY_migrate_channel_links.py|migrate_channel_links.py]]
- [[_COMMUNITY_config.py|config.py]]
- [[_COMMUNITY__parse_genres|_parse_genres]]
- [[_COMMUNITY_MovieGrid.jsx|MovieGrid.jsx]]
- [[_COMMUNITY_admin.py|admin.py]]
- [[_COMMUNITY_MovieGrid.jsx|MovieGrid.jsx]]
- [[_COMMUNITY_GenreFilter.jsx|GenreFilter.jsx]]
- [[_COMMUNITY_adminAuth.js|adminAuth.js]]

## God Nodes (most connected - your core abstractions)
1. `MovieQueries` - 18 edges
2. `process_movie()` - 15 edges
3. `request()` - 13 edges
4. `MovieDatabase` - 12 edges
5. `admin_login()` - 12 edges
6. `TaskManager` - 12 edges
7. `_get_tasks()` - 10 edges
8. `admin_refresh()` - 10 edges
9. `mutate()` - 10 edges
10. `react` - 10 edges

## Surprising Connections (you probably didn't know these)
- `main()` --indirect_call--> `TMDBMovie`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --indirect_call--> `Movie`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --indirect_call--> `TelegramMessage`  [INFERRED]
  migrate_to_postgres.py → database/models.py
- `main()` --calls--> `get_db_url()`  [EXTRACTED]
  update_tmdb.py → database/models.py
- `run_test()` --calls--> `clean_title()`  [EXTRACTED]
  test_migration.py → migrate_channel_links.py

## Import Cycles
- None detected.

## Communities (31 total, 7 thin omitted)

### Community 0 - "MovieQueries"
Cohesion: 0.09
Nodes (23): Request, Health-check / welcome endpoint., root(), SecurityHeadersMiddleware, MovieQueries, Any, Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy., get_movie() (+15 more)

### Community 1 - "movies.py"
Cohesion: 0.12
Nodes (24): GenreListResponse, LibraryCreateRequest, LibraryDetailResponse, LibraryListResponse, LibraryResponse, LibraryUpdateRequest, MigrationRequest, MovieDetailResponse (+16 more)

### Community 2 - "App.jsx"
Cohesion: 0.18
Nodes (25): adminCancelTask(), adminCreateLibrary(), adminDeleteLibrary(), adminFetchLibraries(), adminFetchTask(), adminFetchTaskLogs(), adminFetchTasks(), adminMigrateLibrary() (+17 more)

### Community 3 - "process_movie"
Cohesion: 0.20
Nodes (11): Lock, MovieDatabase, clean_title_and_extract_year(), main(), process_movie(), Any, Return a console-safe version of *text* (handles Windows cp1252)., Clean movie titles before searching TMDB and extract release year if available. (+3 more)

### Community 4 - "package.json"
Cohesion: 0.11
Nodes (18): dependencies, react, react-dom, devDependencies, vite, @vitejs/plugin-react, name, private (+10 more)

### Community 5 - "get_db_url"
Cohesion: 0.19
Nodes (14): Base, get_db_url(), init_db(), Library, Movie, Helper to determine the database URL, Initializes the database and returns the sessionmaker., TelegramMessage (+6 more)

### Community 6 - "tmdb_service.py"
Cohesion: 0.36
Nodes (10): main(), build_poster_url(), _choose_best_match(), get_movie_details(), _normalize_title(), Any, Search TMDB by movie title and return the best matching result.      Returned, Fetch detailed TMDB metadata for a movie.      Returned keys:     - poster_pa (+2 more)

### Community 7 - ".oxlintrc.json"
Cohesion: 0.11
Nodes (13): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, App(), Hero(), HERO_MOVIES (+5 more)

### Community 14 - "config.py"
Cohesion: 0.14
Nodes (15): Message, _clean_title(), extract_movie_title(), _extract_quality(), _is_valid_title(), parse_movie_message(), ParsedMovie, Extract a likely movie title and supported video quality from a Telegram message (+7 more)

### Community 15 - "_parse_genres"
Cohesion: 0.26
Nodes (4): MovieDatabase, SQLAlchemy repository for storing scraped Telegram movie records., Return the set of all Telegram message IDs already stored., Session

### Community 19 - "TaskManager"
Cohesion: 0.14
Nodes (12): Any, task_manager.py — In-memory background task manager.  Spawns CLI scripts (main.p, Launch update_tmdb.py for a specific library., Launch migrate_channel_links.py for a specific library., Manages background subprocess tasks with log capture., Launch main.py scraper for a specific library., TaskInfo, TaskManager (+4 more)

### Community 20 - "migrate_channel_links.py"
Cohesion: 0.09
Nodes (24): _path_env(), Path, Settings, fix_message_id_constraint.py — One-time schema migration.  Removes the old UNIQU, build_match_indexes(), clean_title(), extract_title_from_message(), main() (+16 more)

### Community 21 - "config.py"
Cohesion: 0.25
Nodes (7): get_database_path(), get_database_url(), get_telegram_channel_id(), Path, Resolve the database path from the environment.      Keeps the backend indepen, Get the database URL from the environment for SQLAlchemy., Return the numeric Telegram channel ID (without the ``-100`` prefix).      Use

### Community 22 - "_parse_genres"
Cohesion: 0.10
Nodes (36): AdminInfoResponse, block_refresh_token(), check_rate_limit(), create_access_token(), create_refresh_token(), decode_token(), get_current_admin(), is_refresh_blocked() (+28 more)

### Community 24 - "admin.py"
Cohesion: 0.12
Nodes (30): admin_cancel_task(), admin_create_library(), admin_delete_library(), admin_get_task(), admin_get_task_logs(), admin_list_libraries(), admin_list_tasks(), admin_migrate_library() (+22 more)

### Community 30 - "adminAuth.js"
Cohesion: 0.26
Nodes (14): decodeTokenPayload(), getAccessToken(), getAuthHeaders(), getAuthHeadersAsync(), getRefreshToken(), getUsername(), isAuthenticated(), isTokenExpired() (+6 more)

## Knowledge Gaps
- **19 isolated node(s):** `HERO_MOVIES`, `GENRE_MAP`, `GENRE_MAP`, `Settings`, `$schema` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MovieDatabase` connect `_parse_genres` to `get_db_url`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **What connects `Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy.`, `Accept a JSON string or a plain list and always return ``list[str]``.`, `Body for launching a channel scan.` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MovieQueries` be split into smaller, more focused modules?**
  _Cohesion score 0.0873015873015873 - nodes in this community are weakly interconnected._
- **Should `movies.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1206896551724138 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `.oxlintrc.json` be split into smaller, more focused modules?**
  _Cohesion score 0.10869565217391304 - nodes in this community are weakly interconnected._
- **Should `config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._