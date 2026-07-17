/**
 * Admin authentication client utilities.
 * Handles storage of access and refresh tokens, token expiration, and API auto-refresh.
 */

// Use sessionStorage for tab-scoped storage (safer from XSS than localStorage, cleared on close)
const ACCESS_TOKEN_KEY = 'admin_access_token';
const REFRESH_TOKEN_KEY = 'admin_refresh_token';
const USERNAME_KEY = 'admin_username';
// localStorage key used solely for cross-tab logout signaling
const LOGOUT_SIGNAL_KEY = 'admin_logout_signal';

let refreshPromise = null;

export function getAccessToken() {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return sessionStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getUsername() {
  return sessionStorage.getItem(USERNAME_KEY);
}

export function setTokens(access, refresh, username) {
  if (access) sessionStorage.setItem(ACCESS_TOKEN_KEY, access);
  else sessionStorage.removeItem(ACCESS_TOKEN_KEY);

  if (refresh) sessionStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  else sessionStorage.removeItem(REFRESH_TOKEN_KEY);

  if (username) sessionStorage.setItem(USERNAME_KEY, username);
  else sessionStorage.removeItem(USERNAME_KEY);
}

/**
 * Decode JWT payload without verifying signature (client-side expiry check only).
 * @returns {object|null} decoded payload, or null on failure
 */
function decodeTokenPayload(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    return payload;
  } catch {
    return null;
  }
}

/**
 * Check if a JWT access token is expired (with 30s safety margin).
 */
function isTokenExpired(token) {
  const payload = decodeTokenPayload(token);
  if (!payload || !payload.exp) return true;
  // 30-second buffer to avoid edge-case failures
  return Date.now() / 1000 >= payload.exp - 30;
}

export function isAuthenticated() {
  const token = getAccessToken();
  if (!token) return false;
  // If access token is expired, don't consider authenticated
  // (the refresh flow will handle renewal)
  if (isTokenExpired(token)) return false;
  return true;
}

export function logout() {
  const refresh = getRefreshToken();
  const isLocal = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' || 
                  window.location.hostname.startsWith('192.168.') || 
                  window.location.hostname.startsWith('10.');

  const BASE = isLocal
    ? `http://${window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname}:8000/api/admin`
    : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library.onrender.com') + '/api/admin';

  if (refresh) {
    fetch(`${BASE}/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    }).catch(err => console.error('Logout request failed:', err));
  }

  setTokens(null, null, null);

  // Signal other tabs to clear their session too
  try {
    localStorage.setItem(LOGOUT_SIGNAL_KEY, Date.now().toString());
    localStorage.removeItem(LOGOUT_SIGNAL_KEY);
  } catch {
    // localStorage may be unavailable in some contexts
  }
}

/**
 * Set up cross-tab logout listener. Call once at app startup.
 * When another tab logs out, this tab clears its session too.
 * @param {function} onLogout - callback to run when logout signal received
 */
export function setupStorageListener(onLogout) {
  const handler = (event) => {
    if (event.key === LOGOUT_SIGNAL_KEY && event.newValue) {
      setTokens(null, null, null);
      if (onLogout) onLogout();
    }
  };
  window.addEventListener('storage', handler);
  return () => window.removeEventListener('storage', handler);
}

/**
 * Perform login and return user details.
 */
export async function login(username, password) {
  const isLocal = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' || 
                  window.location.hostname.startsWith('192.168.') || 
                  window.location.hostname.startsWith('10.');

  const BASE = isLocal
    ? `http://${window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname}:8000/api/admin`
    : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library.onrender.com') + '/api/admin';

  const res = await fetch(`${BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    let detail = 'Login failed';
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.detail || detail;
    } catch {
      detail = errorText || detail;
    }
    throw new Error(detail);
  }

  const data = await res.json();
  setTokens(data.access_token, data.refresh_token, username);
  return { username };
}

/**
 * Attempts to obtain a new access token using the refresh token.
 * Prevents multiple concurrent refresh calls by returning the same promise.
 */
export async function refreshAccessToken() {
  if (refreshPromise) {
    return refreshPromise;
  }

  const refresh = getRefreshToken();
  if (!refresh) {
    setTokens(null, null, null);
    return null;
  }

  const isLocal = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' || 
                  window.location.hostname.startsWith('192.168.') || 
                  window.location.hostname.startsWith('10.');

  const BASE = isLocal
    ? `http://${window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname}:8000/api/admin`
    : (import.meta.env.VITE_API_URL || 'https://telegram-movie-library.onrender.com') + '/api/admin';

  refreshPromise = (async () => {
    try {
      const res = await fetch(`${BASE}/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });

      if (!res.ok) {
        throw new Error('Refresh token invalid/expired');
      }

      const data = await res.json();
      setTokens(data.access_token, data.refresh_token, getUsername());
      return data.access_token;
    } catch (err) {
      console.warn('Token refresh failed, logging out:', err);
      setTokens(null, null, null);
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * Returns auth headers if access token is available.
 * If the access token is expired, triggers a silent refresh first.
 */
export async function getAuthHeadersAsync() {
  let token = getAccessToken();
  if (token && isTokenExpired(token)) {
    token = await refreshAccessToken();
  }
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Returns auth headers synchronously (for backward compatibility).
 * Does NOT check expiry — use getAuthHeadersAsync when possible.
 */
export function getAuthHeaders() {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

