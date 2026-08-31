/**
 * API client — thin wrapper around fetch for the /api endpoints.
 */
import { getAuthHeaders, getAuthHeadersAsync, refreshAccessToken } from './adminAuth';

// Use 127.0.0.1 to avoid Windows localhost IPv6 resolution issues
const isLocal = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1' || 
                window.location.hostname.startsWith('192.168.') || 
                window.location.hostname.startsWith('10.');

const BASE = isLocal
  ? '/api'
  : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library-production.up.railway.app') + '/api';

async function request(path, params = {}, retry = true) {
  let targetUrl;
  if (path.startsWith('http://') || path.startsWith('https://')) {
    targetUrl = new URL(path);
  } else {
    targetUrl = new URL(path, window.location.origin);
  }

  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      targetUrl.searchParams.set(key, value);
    }
  });

  const headers = {};
  if (path.includes('/api/admin')) {
    Object.assign(headers, getAuthHeaders());
  }

  let response;
  try {
    response = await fetch(targetUrl.toString(), { headers });
  } catch (err) {
    if (retry) {
      // Retry once after 2.5s if network failed (e.g. Render server waking up from sleep)
      await new Promise((r) => setTimeout(r, 2500));
      try {
        response = await fetch(targetUrl.toString(), { headers });
      } catch (retryErr) {
        throw retryErr;
      }
    } else {
      throw err;
    }
  }

  if (response.status === 401 && retry && path.includes('/api/admin')) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      const retryResponse = await fetch(targetUrl.toString(), { headers });
      if (!retryResponse.ok) {
        throw new Error(`API error ${retryResponse.status}: ${retryResponse.statusText}`);
      }
      return retryResponse.json();
    }
  }

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
export function fetchMovie(id, { language } = {}) {
  return request(`${BASE}/movies/${id}`, { language: language || null });
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
  ? '/api/admin'
  : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library-production.up.railway.app') + '/api/admin';

async function mutate(url, method = 'POST', body = null, retry = true) {
  const options = { method, headers: {} };
  if (body !== null) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }
  if (url.includes('/api/admin')) {
    Object.assign(options.headers, getAuthHeaders());
  }

  const response = await fetch(url, options);
  if (response.status === 401 && retry && url.includes('/api/admin')) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      options.headers['Authorization'] = `Bearer ${newToken}`;
      const retryResponse = await fetch(url, options);
      if (method === 'DELETE' && retryResponse.status === 204) return null;
      if (!retryResponse.ok) {
        const text = await retryResponse.text().catch(() => '');
        throw new Error(`API error ${retryResponse.status}: ${text || retryResponse.statusText}`);
      }
      return retryResponse.json();
    }
  }

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

/** Admin: batch reorder libraries. */
export function adminReorderLibraries(idsOrItems) {
  const payload = Array.isArray(idsOrItems) && typeof idsOrItems[0] === 'number'
    ? { ids: idsOrItems }
    : { items: idsOrItems };
  return mutate(`${ADMIN}/libraries/reorder`, 'PUT', payload);
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

/** Admin: launch TV channel migration. */
export function adminMigrateTVLibrary(id, data) {
  return mutate(`${ADMIN}/tv-libraries/${id}/migrate`, 'POST', data);
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

// ---------------------------------------------------------------------------
// TV Series API helpers (public)
// ---------------------------------------------------------------------------

/** All active TV libraries with series counts. */
export function fetchTVLibraries() {
  return request(`${BASE}/tv-libraries`);
}

/** Single TV library by slug. */
export function fetchTVLibrary(slug) {
  return request(`${BASE}/tv-libraries/${slug}`);
}

/** Paginated TV series list. */
export function fetchSeries({ page = 1, pageSize = 20, search, genre, sortBy, sortOrder, libraryId } = {}) {
  return request(`${BASE}/series`, {
    page,
    page_size: pageSize,
    search: search || null,
    genre: genre || null,
    sort_by: sortBy || null,
    sort_order: sortOrder || null,
    library_id: libraryId || null,
  });
}

/** Single TV series detail. */
export function fetchSeriesDetail(id, { language } = {}) {
  return request(`${BASE}/series/${id}`, { language: language || null });
}

/** All unique genres for TV series. */
export function fetchSeriesGenres({ libraryId } = {}) {
  return request(`${BASE}/series-genres`, {
    library_id: libraryId || null,
  });
}

/** TV series statistics. */
export function fetchSeriesStats({ libraryId } = {}) {
  return request(`${BASE}/series-stats`, {
    library_id: libraryId || null,
  });
}

// ---------------------------------------------------------------------------
// TV Series Admin API helpers
// ---------------------------------------------------------------------------

/** Admin: list ALL TV libraries with detailed stats. */
export function adminFetchTVLibraries() {
  return request(`${ADMIN}/tv-libraries`);
}

/** Admin: create TV library. */
export function adminCreateTVLibrary(data) {
  return mutate(`${ADMIN}/tv-libraries`, 'POST', data);
}

/** Admin: update TV library. */
export function adminUpdateTVLibrary(id, data) {
  return mutate(`${ADMIN}/tv-libraries/${id}`, 'PUT', data);
}

/** Admin: batch reorder TV libraries. */
export function adminReorderTVLibraries(idsOrItems) {
  const payload = Array.isArray(idsOrItems) && typeof idsOrItems[0] === 'number'
    ? { ids: idsOrItems }
    : { items: idsOrItems };
  return mutate(`${ADMIN}/tv-libraries/reorder`, 'PUT', payload);
}

/** Admin: delete TV library. */
export function adminDeleteTVLibrary(id) {
  return mutate(`${ADMIN}/tv-libraries/${id}`, 'DELETE');
}

/** Admin: launch scan for TV library. */
export function adminScanTVLibrary(id) {
  return mutate(`${ADMIN}/tv-libraries/${id}/scan`, 'POST');
}

/** Admin: launch TMDB update for TV library. */
export function adminUpdateTVTmdb(id) {
  return mutate(`${ADMIN}/tv-libraries/${id}/update-tmdb`, 'POST');
}

// ---------------------------------------------------------------------------
// Featured TV Series & Media Upload APIs
// ---------------------------------------------------------------------------

/** Public: fetch all featured/trending TV series. */
export function fetchFeaturedTVSeries() {
  return request(`${BASE}/featured-tv`);
}

/** Admin: list all featured TV series entries. */
export function adminFetchFeaturedTVSeries() {
  return request(`${ADMIN}/featured-tv`);
}

/** Admin: create a new featured TV series entry. */
export function adminCreateFeaturedTVSeries(data) {
  return mutate(`${ADMIN}/featured-tv`, 'POST', data);
}

/** Admin: update a featured TV series entry. */
export function adminUpdateFeaturedTVSeries(id, data) {
  return mutate(`${ADMIN}/featured-tv/${id}`, 'PUT', data);
}

/** Admin: delete a featured TV series entry. */
export function adminDeleteFeaturedTVSeries(id) {
  return mutate(`${ADMIN}/featured-tv/${id}`, 'DELETE');
}

/** Admin: upload an image file (returns { url: '/uploads/xxx.png' }). */
export async function adminUploadImage(formData) {
  const authHeaders = await getAuthHeadersAsync();
  const res = await fetch(`${ADMIN}/upload-image`, {
    method: 'POST',
    headers: {
      ...authHeaders,
    },
    body: formData,
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Upload error HTTP ${res.status}`);
  }
  return res.json();
}

/** Helper to format image URLs (e.g. resolve relative /uploads/ URLs to full backend URL). */
export function formatImageUrl(url) {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url;
  }
  if (url.startsWith('/uploads') || url.startsWith('uploads/')) {
    const cleanPath = url.startsWith('/') ? url : `/${url}`;
    const host = window.location.hostname || '127.0.0.1';
    const isLocal = host === 'localhost' || 
                    host === '127.0.0.1' || 
                    host.startsWith('192.168.') || 
                    host.startsWith('10.');
    const backendBase = isLocal
      ? `http://${host}:8000`
      : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library-production.up.railway.app');
    return `${backendBase}${cleanPath}`;
  }
  return url;
}

// ---------------------------------------------------------------------------
// Visitor Analytics APIs
// ---------------------------------------------------------------------------

/** Public: send a page visit tracking beacon. */
export function trackVisit(data) {
  const trackBase = isLocal ? '/api' : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library-production.up.railway.app') + '/api';
  return fetch(`${trackBase}/track`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    keepalive: true,
  }).catch(() => {});
}

/** Admin: analytics summary (total, unique, active today/week/month). */
export function adminFetchAnalyticsSummary() {
  return request(`${ADMIN}/analytics/summary`);
}

/** Admin: paginated visitor list. */
export function adminFetchAnalyticsVisitors({ page = 1, pageSize = 50 } = {}) {
  return request(`${ADMIN}/analytics/visitors`, { page, page_size: pageSize });
}

/** Admin: breakdown by country/device/OS/browser/page. */
export function adminFetchAnalyticsBreakdown() {
  return request(`${ADMIN}/analytics/breakdown`);
}

/** Admin: daily + monthly chart data. */
export function adminFetchAnalyticsCharts() {
  return request(`${ADMIN}/analytics/charts`);
}
