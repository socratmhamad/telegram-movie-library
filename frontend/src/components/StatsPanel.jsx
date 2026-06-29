export default function StatsPanel({ stats }) {
  if (!stats) return null;

  const items = [
    { value: stats.total_movies, label: 'Total Movies' },
    { value: stats.movies_with_tmdb, label: 'With TMDB Data' },
    { value: stats.movies_without_tmdb, label: 'Missing Data' },
    { value: stats.total_messages, label: 'Telegram Messages' },
  ];

  return (
    <div className="stats-bar" id="stats-panel">
      {items.map((item) => (
        <div className="stat-card" key={item.label}>
          <div className="stat-value">{item.value.toLocaleString()}</div>
          <div className="stat-label">{item.label}</div>
        </div>
      ))}
    </div>
  );
}
