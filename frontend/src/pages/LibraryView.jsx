import { useState, useCallback, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useMovies } from '../hooks/useMovies';
import { fetchLibrary } from '../api/client';
import PublicLayout from '../components/PublicLayout';
import SearchBar from '../components/SearchBar';
import GenreFilter from '../components/GenreFilter';
import MovieGrid from '../components/MovieGrid';
import Pagination from '../components/Pagination';
import MovieDetail from '../components/MovieDetail';

export default function LibraryView() {
  const { librarySlug } = useParams();
  const [libraryName, setLibraryName] = useState('');

  const {
    movies,
    total,
    page,
    setPage,
    totalPages,
    loading,
    error,
    search,
    setSearch,
    genre,
    setGenre,
    genres,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
  } = useMovies(librarySlug);

  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const closeDetail = useCallback(() => setSelectedMovieId(null), []);

  // Fetch library name
  useEffect(() => {
    if (!librarySlug) return;
    fetchLibrary(librarySlug)
      .then((lib) => setLibraryName(lib.name || librarySlug))
      .catch(() => setLibraryName(librarySlug));
  }, [librarySlug]);

  return (
    <PublicLayout>
      <div className="browse-container">
        <motion.div
          className="browse-header"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div>
            <Link to="/" className="browse-back-btn" id="back-to-libraries">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5" />
                <path d="M12 19l-7-7 7-7" />
              </svg>
              العودة إلى المكتبات
            </Link>
            <h1 className="browse-library-name">{libraryName}</h1>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <SearchBar
            search={search}
            onSearchChange={setSearch}
            sortBy={sortBy}
            onSortByChange={setSortBy}
            sortOrder={sortOrder}
            onSortOrderChange={setSortOrder}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
        >
          <GenreFilter genres={genres} activeGenre={genre} onToggle={setGenre} />
        </motion.div>

        <MovieGrid
          movies={movies}
          loading={loading}
          error={error}
          onMovieClick={setSelectedMovieId}
        />

        <Pagination
          page={page}
          totalPages={totalPages}
          total={total}
          onPageChange={setPage}
        />

        <AnimatePresence>
          {selectedMovieId !== null && (
            <MovieDetail
              librarySlug={librarySlug}
              movieId={selectedMovieId}
              onClose={closeDetail}
            />
          )}
        </AnimatePresence>
      </div>
    </PublicLayout>
  );
}
