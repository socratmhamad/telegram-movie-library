import MovieCard from './MovieCard';

export default function MovieGrid({ movies, loading, error, onMovieClick, lang = 'en' }) {
  const isAr = lang === 'ar';

  if (error) {
    return <div className="error-banner" id="error-banner">⚠ {error}</div>;
  }

  if (loading) {
    return (
      <div className="loading-spinner" id="loading-spinner">
        <div className="spinner" />
      </div>
    );
  }

  if (!movies || movies.length === 0) {
    return (
      <div className="empty-state" id="empty-state">
        <div className="empty-state-icon">🎞️</div>
        <div className="empty-state-text">{isAr ? 'لم يتم العثور على أفلام' : 'No movies found'}</div>
        <div className="empty-state-sub">
          {isAr ? 'حاول تعديل البحث أو الفلاتر' : 'Try adjusting your search or filters'}
        </div>
      </div>
    );
  }

  return (
    <div className="movie-grid" id="movie-grid">
      {movies.map((movie) => (
        <MovieCard key={movie.id} movie={movie} onClick={onMovieClick} lang={lang} />
      ))}
    </div>
  );
}
