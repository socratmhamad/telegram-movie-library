import { motion } from 'framer-motion';

export default function MovieCard({ movie, onClick }) {
  const year = movie.release_date ? movie.release_date.slice(0, 4) : null;
  const rating = movie.vote_average != null ? movie.vote_average.toFixed(1) : null;

  // Arabic-ready: prefer Arabic title fields when available in the future
  // movie.title_ar / movie.title fallback
  const displayTitle = movie.title_ar || movie.title;

  return (
    <motion.div
      className="movie-card"
      onClick={() => onClick(movie.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick(movie.id)}
      id={`movie-card-${movie.id}`}
      whileHover={{ y: -6, scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 200, damping: 18 }}
    >
      {movie.poster_url ? (
        <img
          className="movie-card-poster"
          src={movie.poster_url}
          alt={displayTitle}
          loading="lazy"
        />
      ) : (
        <div className="movie-card-no-poster" aria-label="لا يوجد ملصق">
          🎬
        </div>
      )}

      {rating && (
        <div className="movie-card-rating-badge">
          ★ {rating}
        </div>
      )}

      <div className="movie-card-overlay">
        <div className="movie-card-title">{displayTitle}</div>
        <div className="movie-card-meta">
          {year && <span className="movie-card-year">{year}</span>}
          {movie.runtime && <span>{movie.runtime} دقيقة</span>}
        </div>
      </div>
    </motion.div>
  );
}
