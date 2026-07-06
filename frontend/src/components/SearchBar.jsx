export default function SearchBar({ search, onSearchChange, sortBy, onSortByChange, sortOrder, onSortOrderChange }) {
  return (
    <div className="controls-bar" id="search-bar">
      <div className="search-input-wrapper">
        <span className="search-icon" aria-hidden="true">🔍</span>
        <input
          id="search-input"
          className="search-input"
          type="text"
          placeholder="ابحث عن فيلم..."
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
        aria-label="ترتيب حسب"
      >
        <option value="title">الترتيب: العنوان</option>
        <option value="release_date">الترتيب: تاريخ الإصدار</option>
        <option value="vote_average">الترتيب: التقييم</option>
        <option value="runtime">الترتيب: المدة</option>
      </select>

      <select
        id="sort-order-select"
        className="sort-select"
        value={sortOrder}
        onChange={(e) => onSortOrderChange(e.target.value)}
        aria-label="اتجاه الترتيب"
      >
        <option value="asc">تصاعدي</option>
        <option value="desc">تنازلي</option>
      </select>
    </div>
  );
}
