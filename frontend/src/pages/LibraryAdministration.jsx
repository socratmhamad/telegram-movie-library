import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchLibrary, fetchStats, fetchTelegramStatus, testTelegramConnection, importLibrary, updateTelegramLinks } from '../api/client';

export default function LibraryAdministration() {
  const { librarySlug } = useParams();
  const [library, setLibrary] = useState(null);
  const [stats, setStats] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [testResult, setTestResult] = useState(null);
  const [isTesting, setIsTesting] = useState(false);

  useEffect(() => {
    loadData();
    // Poll task status every 2 seconds if a task is running
    const interval = setInterval(loadTaskStatus, 2000);
    return () => clearInterval(interval);
  }, [librarySlug]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [libData, statsData] = await Promise.all([
        fetchLibrary(librarySlug),
        fetchStats(librarySlug)
      ]);
      setLibrary(libData);
      setStats(statsData);
      await loadTaskStatus();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTaskStatus = async () => {
    try {
      const data = await fetchTelegramStatus(librarySlug);
      setTaskStatus(data);
    } catch (err) {
      console.error("Failed to load task status", err);
    }
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await testTelegramConnection(librarySlug);
      setTestResult({ success: true, message: res.message });
    } catch (err) {
      setTestResult({ success: false, message: err.message });
    } finally {
      setIsTesting(false);
    }
  };

  const handleAction = async (action) => {
    try {
      if (action === 'import') {
        await importLibrary(librarySlug);
      } else {
        await updateTelegramLinks(librarySlug);
      }
      loadTaskStatus();
    } catch (err) {
      alert("Failed to start task: " + err.message);
    }
  };

  if (loading) return <div>Loading administration...</div>;
  if (error) return <div className="error-banner">{error}</div>;
  if (!library) return <div>Library not found</div>;

  const isRunning = taskStatus?.status === 'running';

  return (
    <div className="home-container">
      <div className="home-header">
        <h1 className="home-title">{library.name} Administration</h1>
        <Link to={`/admin/libraries/${librarySlug}/settings`} className="btn-create" style={{ backgroundColor: 'var(--text-muted)' }}>
          ⚙️ Settings
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        
        {/* Overview Panel */}
        <div className="panel" style={{ backgroundColor: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
          <h2 style={{ marginBottom: '1rem', color: 'var(--accent-teal)' }}>Overview</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.2rem' }}>Telegram Channel</p>
              <p style={{ fontWeight: 'bold' }}>{library.telegram_channel}</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.2rem' }}>Status</p>
              <p style={{ fontWeight: 'bold' }}>{library.is_active ? 'Active' : 'Disabled'}</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.2rem' }}>Total Movies</p>
              <p style={{ fontWeight: 'bold', fontSize: '1.2rem', color: 'var(--accent-gold)' }}>{stats?.total_movies || 0}</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.2rem' }}>Total Messages</p>
              <p style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>{stats?.total_messages || 0}</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.2rem' }}>Last Scan</p>
              <p>{library.last_scan ? new Date(library.last_scan).toLocaleString() : 'Never'}</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.2rem' }}>Last Migration</p>
              <p>{library.last_migration ? new Date(library.last_migration).toLocaleString() : 'Never'}</p>
            </div>
          </div>

          <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button 
              onClick={handleTestConnection} 
              disabled={isTesting || isRunning}
              className="btn-create" 
              style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--text-muted)' }}
            >
              {isTesting ? 'Testing...' : 'Test Connection'}
            </button>
            <button 
              onClick={() => handleAction('import')} 
              disabled={isRunning}
              className="btn-create" 
              style={{ backgroundColor: 'var(--accent-teal)' }}
            >
              Import Library
            </button>
            <button 
              onClick={() => handleAction('update-links')} 
              disabled={isRunning}
              className="btn-create" 
              style={{ backgroundColor: 'var(--accent-purple)' }}
            >
              Update Telegram Links
            </button>
          </div>
          
          {testResult && (
            <div style={{ marginTop: '1rem', padding: '1rem', borderRadius: '4px', backgroundColor: testResult.success ? 'rgba(45,212,191,0.1)' : 'rgba(239,68,68,0.1)', color: testResult.success ? 'var(--accent-teal)' : '#fca5a5' }}>
              {testResult.success ? '✓ ' : '✗ '} {testResult.message}
            </div>
          )}
        </div>

        {/* Activity Panel */}
        <div className="panel" style={{ backgroundColor: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
          <h2 style={{ marginBottom: '1rem', color: 'var(--accent-purple)' }}>Recent Activity</h2>
          
          {!taskStatus || taskStatus.status === 'idle' ? (
            <p style={{ color: 'var(--text-muted)' }}>No recent task activity.</p>
          ) : (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span style={{ fontWeight: 'bold', textTransform: 'uppercase' }}>
                  {taskStatus.mode === 'import' ? 'Import Library' : 'Update Telegram Links'}
                </span>
                <span style={{ 
                  padding: '0.2rem 0.6rem', 
                  borderRadius: '4px', 
                  backgroundColor: taskStatus.status === 'running' ? 'var(--accent-gold-soft)' : (taskStatus.status === 'error' ? 'rgba(239,68,68,0.2)' : 'var(--accent-teal-soft)'),
                  color: taskStatus.status === 'running' ? 'var(--accent-gold)' : (taskStatus.status === 'error' ? '#fca5a5' : 'var(--accent-teal)'),
                  fontSize: '0.8rem',
                  fontWeight: 'bold'
                }}>
                  {taskStatus.status}
                </span>
              </div>
              
              <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                <li style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ color: 'var(--accent-teal)' }}>✓</span>
                  <span>{taskStatus.total_scanned} messages scanned</span>
                </li>
                
                {taskStatus.mode === 'import' && (
                  <>
                    <li style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span style={{ color: 'var(--accent-teal)' }}>✓</span>
                      <span>{taskStatus.new_movies_added || 0} movies parsed</span>
                    </li>
                    <li style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span style={{ color: 'var(--accent-teal)' }}>✓</span>
                      <span>{taskStatus.tmdb_lookups_completed || 0} TMDB records created</span>
                    </li>
                  </>
                )}

                {taskStatus.mode === 'update_links' && (
                  <>
                    <li style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span style={{ color: 'var(--accent-teal)' }}>✓</span>
                      <span>{taskStatus.matched_movies} existing movies matched</span>
                    </li>
                    <li style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span style={{ color: 'var(--accent-purple)' }}>✓</span>
                      <span>{taskStatus.updated_links} telegram links updated</span>
                    </li>
                  </>
                )}
                
                <li style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ color: 'var(--accent-gold)' }}>ℹ</span>
                  <span>{taskStatus.missing_movies?.length || 0} missing/ignored movies</span>
                </li>
                
                <li style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '0.5rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>⏱</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Executed in {taskStatus.execution_time?.toFixed(1)}s</span>
                </li>
              </ul>
              
              {taskStatus.error_message && (
                <div style={{ marginTop: '1rem', padding: '1rem', borderRadius: '4px', backgroundColor: 'rgba(239,68,68,0.1)', color: '#fca5a5', fontSize: '0.9rem' }}>
                  <strong>Error:</strong> {taskStatus.error_message}
                </div>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
