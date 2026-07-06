import { Link } from 'react-router-dom';

export default function Layout({ children, currentView, onViewChange, librarySlug }) {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-inner" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <Link to="/" className="logo" id="app-logo" style={{ textDecoration: 'none' }}>
            <span className="logo-icon">🎬</span>
            Telegram Movie Library
          </Link>
        </div>
      </header>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
