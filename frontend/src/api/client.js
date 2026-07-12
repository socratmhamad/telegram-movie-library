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
