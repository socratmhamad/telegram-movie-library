export default function SearchBar({ search, onSearchChange, sortBy, onSortByChange, lang = 'en' }) {
  const isAr = lang === 'ar';
  return (
    <div className="controls-bar" id="search-bar">
      <div className="search-input-wrapper">
        <span className="search-icon" aria-hidden="true">🔍</span>
        <input
          id="search-input"
          className="search-input"
          type="text"
          placeholder={isAr ? 'ابحث عن الأفلام…' : 'Search movies…'}
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          autoComplete="off"
        />
      </div>

      <select
        id="sort-by-select"
        className="sort-select"
        value={sortBy}
        onChange={(e) => onSortByChange(e.target.value)}
        aria-label={isAr ? 'ترتيب حسب' : 'Sort by'}
      >
        <option value="title">{isAr ? 'الترتيب: العنوان' : 'Sort: Title'}</option>
        <option value="release_date">{isAr ? 'الترتيب: تاريخ الإصدار' : 'Sort: Release Date'}</option>
        <option value="vote_average">{isAr ? 'الترتيب: التقييم' : 'Sort: Rating'}</option>
        <option value="runtime">{isAr ? 'الترتيب: مدة العرض' : 'Sort: Runtime'}</option>
      </select>
    </div>
  );
}

