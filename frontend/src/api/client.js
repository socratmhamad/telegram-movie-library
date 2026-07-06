/**
 * API client — thin wrapper around fetch for the /api endpoints.
 */

const BASE = `http://${window.location.hostname}:8000/api`;

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

async function postRequest(path, body = {}) {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

/** Libraries */
export function fetchLibraries() {
  return request(`${BASE}/libraries`);
}

export function createLibrary(name, telegram_channel) {
  return postRequest(`${BASE}/libraries`, { name, telegram_channel });
}

export function fetchLibrary(librarySlug) {
  return request(`${BASE}/libraries/${librarySlug}`);
}

export async function updateLibrary(librarySlug, { name, slug, telegram_channel, telegram_channel_id, is_active }) {
  const response = await fetch(`${BASE}/libraries/${librarySlug}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, slug, telegram_channel, telegram_channel_id, is_active }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

/** Paginated movie list. */
export function fetchMovies(librarySlug, { page = 1, pageSize = 20, search, genre, sortBy, sortOrder } = {}) {
  return request(`${BASE}/libraries/${librarySlug}/movies`, {
    page,
    page_size: pageSize,
    search: search || null,
    genre: genre || null,
    sort_by: sortBy || null,
    sort_order: sortOrder || null,
  });
}

/** Single movie detail. */
export function fetchMovie(librarySlug, id) {
  return request(`${BASE}/libraries/${librarySlug}/movies/${id}`);
}

/** All unique genres. */
export function fetchGenres(librarySlug) {
  return request(`${BASE}/libraries/${librarySlug}/genres`);
}

/** Library statistics. */
export function fetchStats(librarySlug) {
  return request(`${BASE}/libraries/${librarySlug}/stats`);
}

/** Telegram Management */
export function fetchTelegramConfig(librarySlug) {
  return request(`${BASE}/libraries/${librarySlug}/telegram/config`);
}

export function fetchTelegramStatus(librarySlug) {
  return request(`${BASE}/libraries/${librarySlug}/telegram/task-status`);
}

export function testTelegramConnection(librarySlug) {
  return postRequest(`${BASE}/libraries/${librarySlug}/telegram/test-connection`);
}

export function importLibrary(librarySlug) {
  return postRequest(`${BASE}/libraries/${librarySlug}/telegram/import`);
}

export function updateTelegramLinks(librarySlug) {
  return postRequest(`${BASE}/libraries/${librarySlug}/telegram/update-links`);
}

/** Featured movies for homepage hero */
export function fetchFeatured() {
  return request(`${BASE}/featured`);
}
