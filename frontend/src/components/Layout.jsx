export default function Layout({ children, libraryName, onBackToLibraries, onOpenAdmin }) {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-inner">
          <button
            className="logo"
            id="app-logo"
            onClick={onBackToLibraries}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          >
            <span className="logo-icon">🎬</span>
            <span className="logo-text">Telegram Movie Library</span>
          </button>
          {libraryName && (
            <div className="header-library-name">
              <button
                className="header-back-btn"
                onClick={onBackToLibraries}
                title="Back to libraries"
              >
                ←
              </button>
              <span className="header-library-label">{libraryName}</span>
            </div>
          )}
          {onOpenAdmin && (
            <button className="header-admin-btn" onClick={onOpenAdmin} title="Admin Dashboard">
              ⚙️ Admin
            </button>
          )}
        </div>
      </header>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
