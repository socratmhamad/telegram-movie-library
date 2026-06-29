export default function MovieCard({ movie, onClick }) {
  const year = movie.release_date ? movie.release_date.slice(0, 4) : null;
  const rating = movie.vote_average != null ? movie.vote_average.toFixed(1) : null;

  return (
    <div
      className="movie-card"
      onClick={() => onClick(movie.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick(movie.id)}
      id={`movie-card-${movie.id}`}
    >
      {movie.poster_url ? (
        <img
          className="movie-card-poster"
          src={movie.poster_url}
          alt={movie.title}
          loading="lazy"
        />
      ) : (
        <div className="movie-card-no-poster" aria-label="No poster available">
          🎬
        </div>
      )}

      {rating && (
        <div className="movie-card-rating-badge">
          ★ {rating}
        </div>
      )}

      <div className="movie-card-overlay">
        <div className="movie-card-title">{movie.title}</div>
        <div className="movie-card-meta">
          {year && <span className="movie-card-year">{year}</span>}
          {movie.runtime && <span>{movie.runtime} min</span>}
        </div>
      </div>
    </div>
  );
}
