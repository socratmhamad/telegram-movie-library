export default function SearchBar({ search, onSearchChange, sortBy, onSortByChange }) {
  return (
    <div className="controls-bar" id="search-bar">
      <div className="search-input-wrapper">
        <span className="search-icon" aria-hidden="true">🔍</span>
        <input
          id="search-input"
          className="search-input"
          type="text"
          placeholder="Search movies…"
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
        aria-label="Sort by"
      >
        <option value="title">Sort: Title</option>
        <option value="release_date">Sort: Release Date</option>
        <option value="vote_average">Sort: Rating</option>
        <option value="runtime">Sort: Runtime</option>
      </select>
    </div>
  );
}

