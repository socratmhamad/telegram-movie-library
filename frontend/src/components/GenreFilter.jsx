const GENRE_MAP = {
  'Action': 'أكشن',
  'Adventure': 'مغامرة',
  'Animation': 'رسوم متحركة',
  'Comedy': 'كوميديا',
  'Crime': 'جريمة',
  'Documentary': 'وثائقي',
  'Drama': 'دراما',
  'Family': 'عائلي',
  'Fantasy': 'خيال',
  'History': 'تاريخ',
  'Horror': 'رعب',
  'Music': 'موسيقى',
  'Mystery': 'غموض',
  'Romance': 'رومانسية',
  'Science Fiction': 'خيال علمي',
  'TV Movie': 'فيلم تلفزيوني',
  'Thriller': 'إثارة',
  'War': 'حرب',
  'Western': 'غربي'
};

export default function GenreFilter({ genres, activeGenre, onToggle, lang = 'en' }) {
  if (!genres || genres.length === 0) return null;

  const isAr = lang === 'ar';

  return (
    <div className="genre-filter" id="genre-filter">
      <button
        className={`genre-tag ${!activeGenre ? 'active' : ''}`}
        onClick={() => onToggle('')}
        type="button"
      >
        {isAr ? 'الكل' : 'All'}
      </button>
      {genres.map((g) => (
        <button
          key={g}
          className={`genre-tag ${activeGenre === g ? 'active' : ''}`}
          onClick={() => onToggle(g)}
          type="button"
        >
          {isAr ? (GENRE_MAP[g] || g) : g}
        </button>
      ))}
    </div>
  );
}
