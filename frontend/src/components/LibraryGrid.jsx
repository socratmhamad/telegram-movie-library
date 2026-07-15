import { useState, useEffect } from 'react';
import { fetchLibraries } from '../api/client';

export default function LibraryGrid({ onSelectLibrary, lang = 'en' }) {
  const [libraries, setLibraries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isAr = lang === 'ar';

  useEffect(() => {
    fetchLibraries()
      .then((data) => setLibraries(data.libraries))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner" />
      </div>
    );
  }

  if (error) {
    return <div className="error-banner">{isAr ? 'فشل تحميل المكتبات:' : 'Failed to load libraries:'} {error}</div>;
  }

  return (
    <div className="library-landing">
      <div className="library-hero">
        <h1 className="library-hero-title">{isAr ? 'مكتبات الأفلام' : 'Movie Libraries'}</h1>
        <p className="library-hero-sub">
          {isAr ? 'اختر مكتبة لتصفح مجموعتها' : 'Choose a library to browse its collection'}
        </p>
      </div>
      <div className="library-grid">
        {libraries.map((lib) => (
          <button
            key={lib.id}
            className="library-card"
            id={`library-card-${lib.slug}`}
            onClick={() => onSelectLibrary(lib.slug)}
          >
            <div className="library-card-icon">📚</div>
            <h2 className="library-card-name">{lib.name}</h2>
            <div className="library-card-count">
              <span className="library-card-count-number">{lib.movie_count.toLocaleString()}</span>
              <span className="library-card-count-label">
                {isAr ? 'فيلم' : (lib.movie_count === 1 ? 'movie' : 'movies')}
              </span>
            </div>
            {lib.telegram_channel && (
              <div className="library-card-channel" title={lib.telegram_channel}>
                📡 {isAr ? 'قناة تيليجرام' : 'Telegram Channel'}
              </div>
            )}
            <div className="library-card-arrow">{isAr ? '←' : '→'}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

