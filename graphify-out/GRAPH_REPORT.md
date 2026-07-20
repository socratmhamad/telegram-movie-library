# Graph Report - Movis_with_Telegram  (2026-07-20)

## Corpus Check
- 71 files · ~31,335 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 492 nodes · 891 edges · 41 communities (32 shown, 9 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1a529c97`
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
- [[_COMMUNITY_StatsPanel.jsx|StatsPanel.jsx]]
- [[_COMMUNITY_GenreFilter.jsx|GenreFilter.jsx]]
- [[_COMMUNITY_SearchBar.jsx|SearchBar.jsx]]
- [[_COMMUNITY_adminAuth.js|adminAuth.js]]
- [[_COMMUNITY_Session|Session]]
- [[_COMMUNITY_Path|Path]]
- [[_COMMUNITY_config.py|config.py]]
- [[_COMMUNITY_Request|Request]]

## God Nodes (most connected - your core abstractions)
1. `MovieQueries` - 24 edges
2. `Movie` - 17 edges
3. `MovieDatabase` - 17 edges
4. `Library` - 16 edges
5. `process_movie()` - 15 edges
6. `TaskManager` - 14 edges
7. `request()` - 13 edges
8. `TelegramMessage` - 12 edges
9. `admin_login()` - 12 edges
10. `What You Must Do When Invoked` - 12 edges

## Surprising Connections (you probably didn't know these)
- `admin_list_libraries()` --indirect_call--> `Library`  [INFERRED]
  backend/routers/admin.py → database/models.py
- `admin_migrate_library()` --indirect_call--> `Library`  [INFERRED]
  backend/routers/admin.py → database/models.py
- `admin_scan_library()` --indirect_call--> `Library`  [INFERRED]
  backend/routers/admin.py → database/models.py
- `admin_update_library()` --indirect_call--> `Library`  [INFERRED]
  backend/routers/admin.py → database/models.py
- `admin_update_tmdb()` --indirect_call--> `Library`  [INFERRED]
  backend/routers/admin.py → database/models.py

## Import Cycles
- None detected.

## Communities (41 total, 9 thin omitted)

### Community 0 - "MovieQueries"
Cohesion: 0.10
Nodes (35): admin_delete_library(), Delete a library and all associated movies/messages., Base, get_db_url(), init_db(), Library, Movie, Helper to determine the database URL (+27 more)

### Community 1 - "movies.py"
Cohesion: 0.07
Nodes (35): Any, global_exception_handler(), Health-check / welcome endpoint., root(), SecurityHeadersMiddleware, MovieQueries, Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy., GenreListResponse (+27 more)

### Community 2 - "App.jsx"
Cohesion: 0.07
Nodes (53): decodeTokenPayload(), getAccessToken(), getAuthHeaders(), getAuthHeadersAsync(), getRefreshToken(), getUsername(), isAuthenticated(), isTokenExpired() (+45 more)

### Community 3 - "process_movie"
Cohesion: 0.14
Nodes (20): Lock, main(), build_poster_url(), _choose_best_match(), get_movie_details(), _normalize_title(), Any, Search TMDB by movie title and return the best matching result.      Returned (+12 more)

### Community 4 - "package.json"
Cohesion: 0.13
Nodes (14): dependencies, react, react-dom, devDependencies, vite, @vitejs/plugin-react, name, private (+6 more)

### Community 5 - "get_db_url"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 6 - "tmdb_service.py"
Cohesion: 0.17
Nodes (10): caveman, Example output, How to invoke, See also, What it does, Auto-Clarity, Boundaries, Intensity (+2 more)

### Community 7 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 14 - "config.py"
Cohesion: 0.08
Nodes (25): _path_env(), Path, Settings, fix_message_id_constraint.py — One-time schema migration.  Removes the old UNIQU, Return a console-safe version of *text* (handles Windows cp1252)., run(), _safe(), Message (+17 more)

### Community 15 - "_parse_genres"
Cohesion: 0.20
Nodes (9): Database Schema, File Purposes, Notes, Project Structure, Run, Setup, Telegram Movies, Test TMDB (+1 more)

### Community 16 - "Any"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 17 - "Path"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 19 - "TaskManager"
Cohesion: 0.14
Nodes (12): Any, task_manager.py — In-memory background task manager.  Spawns CLI scripts (main.p, Launch update_tmdb.py for a specific library., Launch migrate_channel_links.py for a specific library., Manages background subprocess tasks with log capture., Launch main.py scraper for a specific library., TaskInfo, TaskManager (+4 more)

### Community 20 - "migrate_channel_links.py"
Cohesion: 0.09
Nodes (42): LibraryCreateRequest, LibraryDetailResponse, LibraryUpdateRequest, MigrationRequest, MovieListItem, _parse_genres(), Any, Accept a JSON string or a plain list and always return ``list[str]``. (+34 more)

### Community 22 - "_parse_genres"
Cohesion: 0.10
Nodes (36): AdminInfoResponse, block_refresh_token(), check_rate_limit(), create_access_token(), create_refresh_token(), decode_token(), get_current_admin(), is_refresh_blocked() (+28 more)

### Community 23 - "MovieGrid.jsx"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 24 - "admin.py"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 25 - "MovieGrid.jsx"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 26 - "StatsPanel.jsx"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + Vite

### Community 39 - "config.py"
Cohesion: 0.22
Nodes (9): get_app_env(), get_database_path(), get_database_url(), get_telegram_channel_id(), Path, Return the current application environment (development | production)., Resolve the database path from the environment.      Keeps the backend indepen, Get the database URL from the environment for SQLAlchemy.      Only returns th (+1 more)

## Knowledge Gaps
- **79 isolated node(s):** `Settings`, `$schema`, `plugins`, `react/rules-of-hooks`, `react/only-export-components` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TaskManager` connect `TaskManager` to `migrate_channel_links.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `Movie` connect `MovieQueries` to `migrate_channel_links.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Movie` (e.g. with `admin_delete_library()` and `admin_list_libraries()`) actually correct?**
  _`Movie` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Library` (e.g. with `admin_delete_library()` and `admin_list_libraries()`) actually correct?**
  _`Library` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Health-check / welcome endpoint.`, `Read-only query layer that powers the FastAPI endpoints.      Uses SQLAlchemy.`, `Helper to determine the database URL` to the rest of the system?**
  _149 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MovieQueries` be split into smaller, more focused modules?**
  _Cohesion score 0.10040816326530612 - nodes in this community are weakly interconnected._
- **Should `movies.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06972789115646258 - nodes in this community are weakly interconnected._