import { translateGenre } from '../utils/genreMap';

export default function GenreFilter({ genres, activeGenre, onToggle }) {
  if (!genres || genres.length === 0) return null;

  return (
    <div className="genre-filter" id="genre-filter">
      <button
        className={`genre-tag ${!activeGenre ? 'active' : ''}`}
        onClick={() => onToggle('')}
        type="button"
      >
        الكل
      </button>
      {genres.map((g) => (
        <button
          key={g}
          className={`genre-tag ${activeGenre === g ? 'active' : ''}`}
          onClick={() => onToggle(g)}
          type="button"
        >
          {translateGenre(g)}
        </button>
      ))}
    </div>
  );
}
