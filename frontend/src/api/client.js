/**
 * API client — thin wrapper around fetch for the /api endpoints.
 */

// Use 127.0.0.1 to avoid Windows localhost IPv6 resolution issues
const isLocal = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1' || 
                window.location.hostname.startsWith('192.168.') || 
                window.location.hostname.startsWith('10.');

const BASE = isLocal
  ? `http://${window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname}:8000/api`
  : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library.onrender.com') + '/api';

async function request(path, params = {}) {
  const url = new URL(path);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      url.searchParams.set(key, value);
    }
  });

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

/** All active libraries with movie counts. */
export function fetchLibraries() {
  return request(`${BASE}/libraries`);
}

/** Single library by slug. */
export function fetchLibrary(slug) {
  return request(`${BASE}/libraries/${slug}`);
}

/** Paginated movie list. */
export function fetchMovies({ page = 1, pageSize = 20, search, genre, sortBy, sortOrder, libraryId } = {}) {
  return request(`${BASE}/movies`, {
    page,
    page_size: pageSize,
    search: search || null,
    genre: genre || null,
    sort_by: sortBy || null,
    sort_order: sortOrder || null,
    library_id: libraryId || null,
  });
}

/** Single movie detail. */
export function fetchMovie(id) {
  return request(`${BASE}/movies/${id}`);
}

/** All unique genres. */
export function fetchGenres({ libraryId } = {}) {
  return request(`${BASE}/genres`, {
    library_id: libraryId || null,
  });
}

/** Library statistics. */
export function fetchStats({ libraryId } = {}) {
  return request(`${BASE}/stats`, {
    library_id: libraryId || null,
  });
}

// ---------------------------------------------------------------------------
// Admin API helpers
// ---------------------------------------------------------------------------

const ADMIN = isLocal
  ? `http://${window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname}:8000/api/admin`
  : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library.onrender.com') + '/api/admin';

async function mutate(url, method = 'POST', body = null) {
  const options = { method, headers: {} };
  if (body !== null) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }
  const response = await fetch(url, options);
  if (method === 'DELETE' && response.status === 204) return null;
  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`API error ${response.status}: ${text || response.statusText}`);
  }
  return response.json();
}

/** Admin: list ALL libraries with detailed stats. */
export function adminFetchLibraries() {
  return request(`${ADMIN}/libraries`);
}

/** Admin: create library. */
export function adminCreateLibrary(data) {
  return mutate(`${ADMIN}/libraries`, 'POST', data);
}

/** Admin: update library. */
export function adminUpdateLibrary(id, data) {
  return mutate(`${ADMIN}/libraries/${id}`, 'PUT', data);
}

/** Admin: delete library. */
export function adminDeleteLibrary(id) {
  return mutate(`${ADMIN}/libraries/${id}`, 'DELETE');
}

/** Admin: launch scan for library. */
export function adminScanLibrary(id) {
  return mutate(`${ADMIN}/libraries/${id}/scan`, 'POST');
}

/** Admin: launch TMDB update for library. */
export function adminUpdateTmdb(id) {
  return mutate(`${ADMIN}/libraries/${id}/update-tmdb`, 'POST');
}

/** Admin: launch channel migration. */
export function adminMigrateLibrary(id, data) {
  return mutate(`${ADMIN}/libraries/${id}/migrate`, 'POST', data);
}

/** Admin: list all tasks. */
export function adminFetchTasks() {
  return request(`${ADMIN}/tasks`);
}

/** Admin: get task status. */
export function adminFetchTask(taskId) {
  return request(`${ADMIN}/tasks/${taskId}`);
}

/** Admin: get task logs. */
export function adminFetchTaskLogs(taskId) {
  return request(`${ADMIN}/tasks/${taskId}/logs`);
}

/** Admin: cancel task. */
export function adminCancelTask(taskId) {
  return mutate(`${ADMIN}/tasks/${taskId}/cancel`, 'POST');
}
