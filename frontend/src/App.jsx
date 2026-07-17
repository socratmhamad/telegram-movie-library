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
import AdminLogin from './components/AdminLogin';
import { isAuthenticated, logout, setupStorageListener } from './api/adminAuth';


function App() {
  // Slug-based "routing" via state + URL hash
  const [selectedSlug, setSelectedSlug] = useState(null);
  const [libraryInfo, setLibraryInfo] = useState(null);
  const [loadingInfo, setLoadingInfo] = useState(false);

  // Localization state
  const [lang, setLang] = useState(() => localStorage.getItem('lang') || 'ar');
  const handleToggleLang = useCallback(() => {
    setLang((prev) => {
      const next = prev === 'en' ? 'ar' : 'en';
      localStorage.setItem('lang', next);
      return next;
    });
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  }, [lang]);

  // Cross-tab logout synchronization
  useEffect(() => {
    return setupStorageListener(() => {
      setSelectedSlug('admin/login');
    });
  }, []);

  // Read slug from URL hash or pathname on mount
  useEffect(() => {
    const path = window.location.pathname.replace(/^\//, '');
    const hash = window.location.hash.replace('#/', '').replace('#', '');
    if (path === 'admin/login' || path === 'admin') {
      setSelectedSlug(path);
    } else if (hash) {
      setSelectedSlug(hash);
    }
  }, []);

  // Load library info when slug changes
  useEffect(() => {
    if (!selectedSlug || selectedSlug === 'admin' || selectedSlug === 'admin/login') {
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

  // Sync URL hash or pathname
  useEffect(() => {
    if (selectedSlug === 'admin' || selectedSlug === 'admin/login') {
      window.history.replaceState(null, '', `/${selectedSlug}`);
    } else if (selectedSlug) {
      window.history.replaceState(null, '', `#/${selectedSlug}`);
    } else {
      window.history.replaceState(null, '', '/');
    }
  }, [selectedSlug]);

  // Handle browser back/forward and URL changes
  useEffect(() => {
    const handleLocationChange = () => {
      const path = window.location.pathname.replace(/^\//, '');
      const hash = window.location.hash.replace('#/', '').replace('#', '');
      if (path === 'admin/login' || path === 'admin') {
        setSelectedSlug(path);
      } else {
        setSelectedSlug(hash || null);
      }
    };
    window.addEventListener('hashchange', handleLocationChange);
    window.addEventListener('popstate', handleLocationChange);
    return () => {
      window.removeEventListener('hashchange', handleLocationChange);
      window.removeEventListener('popstate', handleLocationChange);
    };
  }, []);

  const libraryId = libraryInfo?.id ?? null;

  const handleSelectLibrary = useCallback((slug) => {
    setSelectedSlug(slug);
  }, []);

  const handleBackToLibraries = useCallback(() => {
    setSelectedSlug(null);
  }, []);

  // Admin login page
  if (selectedSlug === 'admin/login') {
    return (
      <Layout onBackToLibraries={handleBackToLibraries} lang={lang} onToggleLang={handleToggleLang}>
        <AdminLogin
          lang={lang}
          onLoginSuccess={() => setSelectedSlug('admin')}
          onBack={handleBackToLibraries}
        />
      </Layout>
    );
  }

  // Admin dashboard
  if (selectedSlug === 'admin') {
    if (!isAuthenticated()) {
      setTimeout(() => setSelectedSlug('admin/login'), 0);
      return null;
    }
    return (
      <Layout onBackToLibraries={handleBackToLibraries} lang={lang} onToggleLang={handleToggleLang}>
        <AdminDashboard
          onBack={handleBackToLibraries}
          onLogout={() => {
            logout();
            setSelectedSlug('admin/login');
          }}
          lang={lang}
        />
      </Layout>
    );
  }

  // Landing page: library grid
  if (!selectedSlug) {
    return (
      <Layout onBackToLibraries={handleBackToLibraries} lang={lang} onToggleLang={handleToggleLang}>
        <LibraryGrid onSelectLibrary={handleSelectLibrary} lang={lang} />
      </Layout>
    );
  }

  // Loading library metadata
  if (loadingInfo || !libraryInfo || libraryInfo.slug !== selectedSlug) {
    return (
      <Layout onBackToLibraries={handleBackToLibraries} lang={lang} onToggleLang={handleToggleLang}>
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
      lang={lang}
      onToggleLang={handleToggleLang}
    />
  );
}


function LibraryView({ libraryId, libraryName, onBackToLibraries, lang, onToggleLang }) {
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

  const isAr = lang === 'ar';

  return (
    <Layout libraryName={null} onBackToLibraries={onBackToLibraries} lang={lang} onToggleLang={onToggleLang}>
      <div className="library-view-header">
        <button className="library-back-btn" onClick={onBackToLibraries}>
          <span className="arrow">{isAr ? '←' : '←'}</span>
          <span className="text">{isAr ? 'العودة للمكتبات' : 'Back to Libraries'}</span>
        </button>
        <h1 className="library-title">{libraryName}</h1>
      </div>
      <SearchBar
        search={search}
        onSearchChange={setSearch}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        lang={lang}
      />
      <GenreFilter genres={genres} activeGenre={genre} onToggle={setGenre} lang={lang} />
      <MovieGrid
        movies={movies}
        loading={loading}
        error={error}
        onMovieClick={setSelectedMovieId}
        lang={lang}
      />
      <Pagination
        page={page}
        totalPages={totalPages}
        total={total}
        onPageChange={setPage}
        lang={lang}
      />
      {selectedMovieId !== null && (
        <MovieDetail movieId={selectedMovieId} onClose={closeDetail} lang={lang} />
      )}
    </Layout>
  );
}

export default App;
