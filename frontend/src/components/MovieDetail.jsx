import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { fetchMovie } from '../api/client';
import { translateGenre } from '../utils/genreMap';

export default function MovieDetail({ librarySlug, movieId, onClose }) {
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!movieId || !librarySlug) return;
    setLoading(true);
    setError(null);

    fetchMovie(librarySlug, movieId)
      .then((data) => setMovie(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [librarySlug, movieId]);

  // Close on Escape key
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  // Prevent body scroll
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  const tmdb = movie?.tmdb;

  // Arabic-ready: prefer Arabic fields when available
  const displayTitle = tmdb?.title_ar || movie?.title || '';
  const displayOverview = tmdb?.overview_ar || tmdb?.overview || '';
  const originalTitle = tmdb?.original_title;
  const rating = tmdb?.vote_average != null ? tmdb.vote_average.toFixed(1) : null;
  const year = tmdb?.release_date ? tmdb.release_date.slice(0, 4) : null;

  return (
    <motion.div
      className="modal-overlay"
      onClick={handleOverlayClick}
      id="movie-detail-modal"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.25 }}
    >
      <motion.div
        className="modal-content"
        role="dialog"
        aria-label="تفاصيل الفيلم"
        initial={{ opacity: 0, y: 40, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 30, scale: 0.97 }}
        transition={{ type: 'spring', stiffness: 120, damping: 18 }}
      >
        {/* Premium floating close button */}
        <button className="modal-close-btn" onClick={onClose} aria-label="إغلاق">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        {loading && (
          <div className="modal-loading">
            <div className="modal-loading-spinner">
              <div className="spinner-ring" />
            </div>
            <span className="modal-loading-text">جاري تحميل التفاصيل...</span>
          </div>
        )}

        {error && <div className="error-banner" style={{ margin: '2rem' }}>⚠ {error}</div>}

        {movie && !loading && (
          <>
            {tmdb?.backdrop_url ? (
              <motion.div
                className="modal-backdrop-wrapper"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <img
                  className="modal-backdrop-image"
                  src={tmdb.backdrop_url}
                  alt=""
                />
                <div className="modal-backdrop-fade" />
              </motion.div>
            ) : (
              <div className="modal-backdrop-placeholder" />
            )}

            <div className="modal-body">
              {/* Poster */}
              {tmdb?.poster_url ? (
                <motion.img
                  className="modal-poster"
                  src={tmdb.poster_url}
                  alt={displayTitle}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15, duration: 0.4 }}
                />
              ) : (
                <div className="modal-poster-placeholder">🎬</div>
              )}

              {/* Info */}
              <motion.div
                className="modal-info"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.4 }}
              >
                <h1 className="modal-title">{displayTitle}</h1>

                {originalTitle && originalTitle !== displayTitle && (
                  <div className="modal-original-title">
                    {originalTitle}
                  </div>
                )}

                <div className="modal-meta">
                  {rating && (
                    <span className="modal-rating">★ {rating}</span>
                  )}
                  {year && (
                    <span className="modal-meta-item">
                      <span className="modal-meta-label">السنة</span> {year}
                    </span>
                  )}
                  {tmdb?.runtime && (
                    <span className="modal-meta-item">
                      <span className="modal-meta-label">المدة</span> {tmdb.runtime} دقيقة
                    </span>
                  )}
                  {tmdb?.imdb_id && (
                    <a
                      href={`https://www.imdb.com/title/${tmdb.imdb_id}/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="modal-imdb-link"
                    >
                      IMDb ↗
                    </a>
                  )}
                </div>

                {tmdb?.genres && tmdb.genres.length > 0 && (
                  <div className="modal-genres">
                    {tmdb.genres.map((g) => (
                      <span className="modal-genre-tag" key={g}>{translateGenre(g)}</span>
                    ))}
                  </div>
                )}

                {displayOverview && (
                  <p className="modal-overview">{displayOverview}</p>
                )}

                {movie.telegram_link && (
                  <motion.a
                    className="telegram-watch-btn"
                    href={movie.telegram_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    id="watch-on-telegram-btn"
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                  >
                    📺 شاهد على تيليجرام
                  </motion.a>
                )}
              </motion.div>
            </div>
          </>
        )}
      </motion.div>
    </motion.div>
  );
}
