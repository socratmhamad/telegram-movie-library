import { useState, useEffect } from 'react';
import { fetchMovie } from '../api/client';

export default function MovieDetail({ movieId, onClose }) {
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!movieId) return;
    setLoading(true);
    setError(null);

    fetchMovie(movieId)
      .then((data) => setMovie(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [movieId]);

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
  const rating = tmdb?.vote_average != null ? tmdb.vote_average.toFixed(1) : null;
  const year = tmdb?.release_date ? tmdb.release_date.slice(0, 4) : null;

  return (
    <div className="modal-overlay" onClick={handleOverlayClick} id="movie-detail-modal">
      <div className="modal-content" role="dialog" aria-label="Movie details">
        <button className="modal-close" onClick={onClose} aria-label="Close">✕</button>

        {loading && (
          <div className="loading-spinner" style={{ padding: '4rem' }}>
            <div className="spinner" />
          </div>
        )}

        {error && <div className="error-banner" style={{ margin: '2rem' }}>⚠ {error}</div>}

        {movie && !loading && (
          <>
            {tmdb?.backdrop_url ? (
              <img className="modal-backdrop-img" src={tmdb.backdrop_url} alt="" />
            ) : (
              <div className="modal-backdrop-placeholder" />
            )}

            <div className="modal-body">
              {/* Poster */}
              {tmdb?.poster_url ? (
                <img className="modal-poster" src={tmdb.poster_url} alt={movie.title} />
              ) : (
                <div className="modal-poster-placeholder">🎬</div>
              )}

              {/* Info */}
              <div className="modal-info">
                <h1 className="modal-title">{movie.title}</h1>

                {tmdb?.original_title && tmdb.original_title !== movie.title && (
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.5rem', fontStyle: 'italic' }}>
                    {tmdb.original_title}
                  </div>
                )}

                <div className="modal-meta">
                  {rating && (
                    <span className="modal-rating">★ {rating}</span>
                  )}
                  {year && <span>{year}</span>}
                  {tmdb?.runtime && <span>{tmdb.runtime} min</span>}
                  {tmdb?.imdb_id && (
                    <a
                      href={`https://www.imdb.com/title/${tmdb.imdb_id}/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: 'var(--accent-gold)', textDecoration: 'none', fontWeight: 600 }}
                    >
                      IMDb ↗
                    </a>
                  )}
                </div>

                {tmdb?.genres && tmdb.genres.length > 0 && (
                  <div className="modal-genres">
                    {tmdb.genres.map((g) => (
                      <span className="modal-genre-tag" key={g}>{g}</span>
                    ))}
                  </div>
                )}

                {tmdb?.overview && (
                  <p className="modal-overview">{tmdb.overview}</p>
                )}

                {movie.telegram_link && (
                  <a
                    className="telegram-watch-btn"
                    href={movie.telegram_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    id="watch-on-telegram-btn"
                  >
                    📺 Watch on Telegram
                  </a>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
