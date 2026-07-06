import { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchLibraries, fetchStats, fetchFeatured } from '../api/client';
import { translateGenres } from '../utils/genreMap';
import PublicLayout from '../components/PublicLayout';

// Category icons based on common library name patterns
function getLibraryEmoji(name) {
  const lower = name.toLowerCase();
  if (lower.includes('أنمي') || lower.includes('anime')) return '🎌';
  if (lower.includes('مسلسل') || lower.includes('series') || lower.includes('tv')) return '📺';
  if (lower.includes('وثائقي') || lower.includes('documentary')) return '🎥';
  if (lower.includes('كرتون') || lower.includes('cartoon') || lower.includes('animation')) return '🧸';
  return '🎬';
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12 },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 100, damping: 15 },
  },
};

const HERO_INTERVAL = 7000; // 7 seconds

export default function Home() {
  const [libraries, setLibraries] = useState([]);
  const [libraryStats, setLibraryStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Hero state
  const [featuredMovies, setFeaturedMovies] = useState([]);
  const [heroIndex, setHeroIndex] = useState(0);
  const heroTimer = useRef(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Fetch libraries + featured in parallel
      const [libData, featuredData] = await Promise.all([
        fetchLibraries(),
        fetchFeatured().catch(() => ({ items: [] })),
      ]);

      const libs = libData.libraries || [];
      setLibraries(libs);
      setFeaturedMovies(featuredData.items || []);

      // Fetch stats for each library (non-blocking)
      const statsMap = {};
      await Promise.allSettled(
        libs.map(async (lib) => {
          try {
            const stats = await fetchStats(lib.slug);
            statsMap[lib.slug] = stats;
          } catch {
            // Non-critical
          }
        })
      );
      setLibraryStats(statsMap);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Hero auto-rotation
  const advanceHero = useCallback(() => {
    setHeroIndex((prev) => (prev + 1) % (featuredMovies.length || 1));
  }, [featuredMovies.length]);

  useEffect(() => {
    if (featuredMovies.length <= 1) return;
    heroTimer.current = setInterval(advanceHero, HERO_INTERVAL);
    return () => clearInterval(heroTimer.current);
  }, [advanceHero, featuredMovies.length]);

  const currentMovie = featuredMovies[heroIndex] || null;

  return (
    <PublicLayout>
      {/* ========== CINEMATIC HERO ========== */}
      <section className="cinematic-hero" id="cinematic-hero">
        {/* Backdrop images with Ken Burns */}
        <div className="hero-backdrop-container">
          <AnimatePresence mode="wait">
            {currentMovie && (
              <motion.div
                key={currentMovie.id}
                className="hero-backdrop-slide"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 1.2, ease: 'easeInOut' }}
              >
                <img
                  className="hero-backdrop-img"
                  src={currentMovie.backdrop_url}
                  alt=""
                  loading="eager"
                />
              </motion.div>
            )}
          </AnimatePresence>
          <div className="hero-gradient-overlay" />
        </div>

        {/* Hero content */}
        <div className="hero-content">
          <AnimatePresence mode="wait">
            {currentMovie && (
              <motion.div
                key={currentMovie.id}
                className="hero-text-block"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              >
                <h1 className="hero-movie-title">{currentMovie.title}</h1>

                <div className="hero-meta-row">
                  {currentMovie.vote_average != null && (
                    <span className="hero-rating">
                      <span className="hero-rating-star">★</span>
                      {currentMovie.vote_average.toFixed(1)}
                    </span>
                  )}
                  {currentMovie.release_date && (
                    <span className="hero-year">
                      {currentMovie.release_date.slice(0, 4)}
                    </span>
                  )}
                  {currentMovie.genres && currentMovie.genres.length > 0 && (
                    <span className="hero-genres-inline">
                      {translateGenres(currentMovie.genres).slice(0, 3).join(' · ')}
                    </span>
                  )}
                </div>

                {currentMovie.overview && (
                  <p className="hero-overview">
                    {currentMovie.overview.length > 180
                      ? currentMovie.overview.slice(0, 180) + '...'
                      : currentMovie.overview}
                  </p>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Hero indicators */}
          {featuredMovies.length > 1 && (
            <div className="hero-indicators">
              {featuredMovies.map((_, idx) => (
                <button
                  key={idx}
                  className={`hero-indicator ${idx === heroIndex ? 'active' : ''}`}
                  onClick={() => {
                    setHeroIndex(idx);
                    clearInterval(heroTimer.current);
                    heroTimer.current = setInterval(advanceHero, HERO_INTERVAL);
                  }}
                  aria-label={`الانتقال إلى الفيلم ${idx + 1}`}
                />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ========== LIBRARIES SHOWCASE ========== */}
      <section className="libraries-showcase">
        <motion.h2
          className="libraries-showcase-title"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          المكتبات المتاحة
        </motion.h2>

        {loading && (
          <div className="skeleton-library-grid">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="skeleton-library-card">
                <div className="skeleton-library-art" />
                <div className="skeleton-library-body">
                  <div className="skeleton-line skeleton-line-title" />
                  <div className="skeleton-line skeleton-line-sub" />
                </div>
              </div>
            ))}
          </div>
        )}

        {error && <div className="error-banner">⚠ {error}</div>}

        {!loading && !error && libraries.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">📚</div>
            <div className="empty-state-text">لا توجد مكتبات بعد</div>
            <div className="empty-state-sub">ستظهر المكتبات هنا عند إضافتها</div>
          </div>
        )}

        {!loading && !error && libraries.length > 0 && (
          <motion.div
            className="libraries-showcase-grid"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {libraries.map((lib, index) => {
              const stats = libraryStats[lib.slug];
              const emoji = getLibraryEmoji(lib.name);

              return (
                <motion.div key={lib.id} variants={cardVariants}>
                  <Link
                    to={`/library/${lib.slug}`}
                    className="library-showcase-card"
                    id={`library-card-${lib.slug}`}
                  >
                    <div className="library-card-artwork">
                      <span className="library-card-emoji">{emoji}</span>
                      <div className="library-card-artwork-glow" />
                    </div>
                    <div className="library-card-content">
                      <div className="library-card-name">{lib.name}</div>
                      <div className="library-card-count">
                        {stats
                          ? `${stats.total_movies.toLocaleString('ar-EG')} فيلم`
                          : 'جاري التحميل...'}
                      </div>
                    </div>
                    <div className="library-card-arrow">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M19 12H5" />
                        <path d="M12 19l-7-7 7-7" />
                      </svg>
                    </div>
                  </Link>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </section>
    </PublicLayout>
  );
}
