import { useState, useCallback } from 'react';
import './index.css';
import { useMovies } from './hooks/useMovies';
import Layout from './components/Layout';
import StatsPanel from './components/StatsPanel';
import SearchBar from './components/SearchBar';
import GenreFilter from './components/GenreFilter';
import MovieGrid from './components/MovieGrid';
import Pagination from './components/Pagination';
import MovieDetail from './components/MovieDetail';

function App() {
  const {
    movies,
    total,
    page,
    setPage,
    totalPages,
    loading,
    error,
    search,
    setSearch,
    genre,
    setGenre,
    genres,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    stats,
  } = useMovies();

  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const closeDetail = useCallback(() => setSelectedMovieId(null), []);

  return (
    <Layout>
      <StatsPanel stats={stats} />
      <SearchBar
        search={search}
        onSearchChange={setSearch}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        sortOrder={sortOrder}
        onSortOrderChange={setSortOrder}
      />
      <GenreFilter genres={genres} activeGenre={genre} onToggle={setGenre} />
      <MovieGrid
        movies={movies}
        loading={loading}
        error={error}
        onMovieClick={setSelectedMovieId}
      />
      <Pagination
        page={page}
        totalPages={totalPages}
        total={total}
        onPageChange={setPage}
      />
      {selectedMovieId !== null && (
        <MovieDetail movieId={selectedMovieId} onClose={closeDetail} />
      )}
    </Layout>
  );
}

export default App;
