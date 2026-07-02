/**
 * API client — thin wrapper around fetch for the /api endpoints.
 */

const BASE = 'https://telegram-movie-library.onrender.com/api';

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

/** Paginated movie list. */
export function fetchMovies({ page = 1, pageSize = 20, search, genre, sortBy, sortOrder } = {}) {
  return request(`${BASE}/movies`, {
    page,
    page_size: pageSize,
    search: search || null,
    genre: genre || null,
    sort_by: sortBy || null,
    sort_order: sortOrder || null,
  });
}

/** Single movie detail. */
export function fetchMovie(id) {
  return request(`${BASE}/movies/${id}`);
}

/** All unique genres. */
export function fetchGenres() {
  return request(`${BASE}/genres`);
}

/** Library statistics. */
export function fetchStats() {
  return request(`${BASE}/stats`);
}
