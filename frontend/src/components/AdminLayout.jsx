import { Link, Outlet } from 'react-router-dom';

export default function AdminLayout() {
  return (
    <div className="app-layout">
      <header className="app-header" style={{ borderBottom: '1px solid var(--accent-purple)' }}>
        <div className="header-inner" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <Link to="/" className="logo" style={{ textDecoration: 'none' }}>
            <span className="logo-icon">⚙️</span>
            Administration Dashboard
          </Link>
          <nav style={{ display: 'flex', gap: '1rem' }}>
            <Link 
              to="/"
              style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer', textDecoration: 'none', fontWeight: 'bold' }}
            >
              Exit to App
            </Link>
          </nav>
        </div>
      </header>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
