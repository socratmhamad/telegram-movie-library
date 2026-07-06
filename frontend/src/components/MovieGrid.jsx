import { motion } from 'framer-motion';
import MovieCard from './MovieCard';

const gridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.04 },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.97 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 120, damping: 14 },
  },
};

export default function MovieGrid({ movies, loading, error, onMovieClick }) {
  if (error) {
    return (
      <div className="error-banner" id="error-banner">
        <span className="error-icon">⚠</span>
        <div>
          <div className="error-title">حدث خطأ</div>
          <div className="error-message">{error}</div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="skeleton-grid" id="loading-skeleton">
        {Array.from({ length: 12 }, (_, i) => (
          <div key={i} className="skeleton-card">
            <div className="skeleton-card-poster" />
            <div className="skeleton-card-info">
              <div className="skeleton-line skeleton-line-title" />
              <div className="skeleton-line skeleton-line-sub" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!movies || movies.length === 0) {
    return (
      <motion.div
        className="empty-state"
        id="empty-state"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
      >
        <div className="empty-state-icon">🎞️</div>
        <div className="empty-state-text">لم يتم العثور على أفلام</div>
        <div className="empty-state-sub">جرّب تعديل البحث أو الفلاتر</div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="movie-grid"
      id="movie-grid"
      variants={gridVariants}
      initial="hidden"
      animate="visible"
      key={movies.map(m => m.id).join(',')}
    >
      {movies.map((movie) => (
        <motion.div key={movie.id} variants={cardVariants}>
          <MovieCard movie={movie} onClick={onMovieClick} />
        </motion.div>
      ))}
    </motion.div>
  );
}
