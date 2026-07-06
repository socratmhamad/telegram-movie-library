import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchMovies, fetchGenres, fetchStats } from '../api/client';

/**
 * Central data-fetching hook for the movie library.
 * Manages pagination, search, genre filter, sorting, and stats.
 */
export function useMovies(librarySlug) {
  // --- Movie list state ---
  const [movies, setMovies] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- Filters & sorting ---
  const [search, setSearch] = useState('');
  const [genre, setGenre] = useState('');
  const [sortBy, setSortBy] = useState('title');
  const [sortOrder, setSortOrder] = useState('asc');

  // --- Genres ---
  const [genres, setGenres] = useState([]);

  // --- Stats ---
  const [stats, setStats] = useState(null);

  // Debounce ref for search
  const searchTimer = useRef(null);
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search input
  useEffect(() => {
    clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1); // Reset to page 1 on new search
    }, 350);
    return () => clearTimeout(searchTimer.current);
  }, [search]);

  // Reset page when genre or sort changes
  useEffect(() => {
    setPage(1);
  }, [genre, sortBy, sortOrder]);

  // Fetch movies
  useEffect(() => {
    let cancelled = false;
    if (!librarySlug) return;
    setLoading(true);
    setError(null);

    fetchMovies(librarySlug, {
      page,
      pageSize,
      search: debouncedSearch,
      genre,
      sortBy,
      sortOrder,
    })
      .then((data) => {
        if (cancelled) return;
        setMovies(data.items);
        setTotal(data.total);
        setTotalPages(data.total_pages);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [page, pageSize, debouncedSearch, genre, sortBy, sortOrder]);

  // Fetch genres
  useEffect(() => {
    if (!librarySlug) return;
    fetchGenres(librarySlug)
      .then((data) => setGenres(data.genres))
      .catch(() => {}); // non-critical
  }, [librarySlug]);

  // Fetch stats
  useEffect(() => {
    if (!librarySlug) return;
    fetchStats(librarySlug)
      .then((data) => setStats(data))
      .catch(() => {}); // non-critical
  }, [librarySlug]);

  const clearGenre = useCallback(() => setGenre(''), []);
  const toggleGenre = useCallback((g) => {
    setGenre((prev) => (prev === g ? '' : g));
  }, []);

  return {
    movies,
    total,
    page,
    setPage,
    pageSize,
    totalPages,
    loading,
    error,
    search,
    setSearch,
    genre,
    setGenre: toggleGenre,
    clearGenre,
    genres,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    stats,
  };
}
