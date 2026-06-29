export default function Layout({ children }) {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-inner">
          <div className="logo" id="app-logo">
            <span className="logo-icon">🎬</span>
            Telegram Movie Library
          </div>
        </div>
      </header>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
