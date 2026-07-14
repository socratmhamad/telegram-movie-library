import { useState, useCallback, useEffect } from 'react';
import './index.css';
import { fetchLibrary } from './api/client';
import { useMovies } from './hooks/useMovies';
import Layout from './components/Layout';
import LibraryGrid from './components/LibraryGrid';
import StatsPanel from './components/StatsPanel';
import SearchBar from './components/SearchBar';
import GenreFilter from './components/GenreFilter';
import MovieGrid from './components/MovieGrid';
import Pagination from './components/Pagination';
import MovieDetail from './components/MovieDetail';
import AdminDashboard from './components/AdminDashboard';

function App() {
  // Slug-based "routing" via state + URL hash
  const [selectedSlug, setSelectedSlug] = useState(null);
  const [libraryInfo, setLibraryInfo] = useState(null);
  const [loadingInfo, setLoadingInfo] = useState(false);

  // Read slug from URL hash on mount
  useEffect(() => {
    const hash = window.location.hash.replace('#/', '').replace('#', '');
    if (hash) {
      setSelectedSlug(hash);
    }
  }, []);

  // Load library info when slug changes
  useEffect(() => {
    if (!selectedSlug) {
      setLibraryInfo(null);
      setLoadingInfo(false);
      return;
    }
    setLoadingInfo(true);
    fetchLibrary(selectedSlug)
      .then((data) => {
        setLibraryInfo(data);
        setLoadingInfo(false);
      })
      .catch(() => {
        setLibraryInfo(null);
        setLoadingInfo(false);
      });
  }, [selectedSlug]);

  // Sync URL hash
  useEffect(() => {
    if (selectedSlug) {
      window.history.replaceState(null, '', `#/${selectedSlug}`);
    } else {
      window.history.replaceState(null, '', window.location.pathname);
    }
  }, [selectedSlug]);

  // Handle browser back/forward
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#/', '').replace('#', '');
      setSelectedSlug(hash || null);
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const libraryId = libraryInfo?.id ?? null;

  const handleSelectLibrary = useCallback((slug) => {
    setSelectedSlug(slug);
  }, []);

  const handleBackToLibraries = useCallback(() => {
    setSelectedSlug(null);
  }, []);

  // Admin dashboard
  if (selectedSlug === 'admin') {
    return (
      <Layout onBackToLibraries={handleBackToLibraries}>
        <AdminDashboard onBack={handleBackToLibraries} />
      </Layout>
    );
  }

  // Landing page: library grid
  if (!selectedSlug) {
    return (
      <Layout onBackToLibraries={handleBackToLibraries} onOpenAdmin={() => setSelectedSlug('admin')}>
        <LibraryGrid onSelectLibrary={handleSelectLibrary} />
      </Layout>
    );
  }

  // Loading library metadata
  if (loadingInfo || !libraryInfo || libraryInfo.slug !== selectedSlug) {
    return (
      <Layout onBackToLibraries={handleBackToLibraries}>
        <div className="loading-spinner">
          <div className="spinner" />
        </div>
      </Layout>
    );
  }

  // Library movie view
  return (
    <LibraryView
      libraryId={libraryId}
      libraryName={libraryInfo?.name}
      onBackToLibraries={handleBackToLibraries}
    />
  );
}


function LibraryView({ libraryId, libraryName, onBackToLibraries }) {
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
    stats,
  } = useMovies(libraryId);

  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const closeDetail = useCallback(() => setSelectedMovieId(null), []);

  return (
    <Layout libraryName={libraryName} onBackToLibraries={onBackToLibraries}>
      <StatsPanel stats={stats} />
      <SearchBar
        search={search}
        onSearchChange={setSearch}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        sortOrder={sortOrder}
        onSortOrderChange={setSortOrder}
      />
      <GenreFilter genres={genres} activeGenre={genre} onToggle={setGenre} />
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
      {selectedMovieId !== null && (
        <MovieDetail movieId={selectedMovieId} onClose={closeDetail} />
      )}
    </Layout>
  );
}

export default App;
