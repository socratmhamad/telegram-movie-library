export default function Layout({ children, libraryName, onBackToLibraries, lang = 'en', onToggleLang, hero }) {
  const isAr = lang === 'ar';
  return (
    <div className={`app-layout ${isAr ? 'rtl' : 'ltr'}`}>
      <header className="app-header">
        <div className="header-inner">
          <button
            className="logo"
            id="app-logo"
            onClick={onBackToLibraries}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          >
            <span className="logo-icon">🎬</span>
            <span className="logo-text logo-desktop-text">{isAr ? 'مكتبة أفلام تيليجرام' : 'Telegram Movie Library'}</span>
            <span className="logo-text logo-mobile-text">{isAr ? 'أفلام تيليجرام' : 'Telegram Movies'}</span>
          </button>

          <div className="header-actions" style={{ display: 'flex', gap: '0.75rem', marginLeft: isAr ? '0' : 'auto', marginRight: isAr ? 'auto' : '0' }}>
            <button className="header-lang-btn" onClick={onToggleLang} style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', padding: '0.5rem 1rem', borderRadius: 'var(--radius-sm)', cursor: 'pointer', transition: 'all var(--transition-fast)' }}>
              🌐 {isAr ? 'English' : 'العربية'}
            </button>
          </div>
        </div>
      </header>
      {hero}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}


