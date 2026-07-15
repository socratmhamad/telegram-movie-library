export default function Layout({ children, libraryName, onBackToLibraries, onOpenAdmin, lang = 'en', onToggleLang }) {
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
            <span className="logo-text">{isAr ? 'مكتبة أفلام تيليجرام' : 'Telegram Movie Library'}</span>
          </button>

          <div className="header-actions" style={{ display: 'flex', gap: '0.75rem', marginLeft: isAr ? '0' : 'auto', marginRight: isAr ? 'auto' : '0' }}>
            <button className="header-lang-btn" onClick={onToggleLang} style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', padding: '0.5rem 1rem', borderRadius: 'var(--radius-sm)', cursor: 'pointer', transition: 'all var(--transition-fast)' }}>
              🌐 {isAr ? 'English' : 'العربية'}
            </button>
            {onOpenAdmin && (
              <button className="header-admin-btn" onClick={onOpenAdmin} title={isAr ? 'لوحة الإدارة' : 'Admin Dashboard'}>
                {isAr ? '⚙️ الإدارة' : '⚙️ Admin'}
              </button>
            )}
          </div>
        </div>
      </header>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

