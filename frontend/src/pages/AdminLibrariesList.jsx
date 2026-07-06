import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchLibraries, createLibrary } from '../api/client';

export default function AdminLibrariesList() {
  const [libraries, setLibraries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Form state
  const [isCreating, setIsCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [newChannel, setNewChannel] = useState('');
  const [createError, setCreateError] = useState(null);

  useEffect(() => {
    loadLibraries();
  }, []);

  const loadLibraries = async () => {
    try {
      setLoading(true);
      const data = await fetchLibraries();
      setLibraries(data.libraries || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreateError(null);
    try {
      await createLibrary(newName, newChannel);
      setNewName('');
      setNewChannel('');
      setIsCreating(false);
      loadLibraries();
    } catch (err) {
      setCreateError(err.message);
    }
  };

  if (loading) return <div className="loading-libraries">Loading libraries...</div>;
  if (error) return <div className="error-libraries">{error}</div>;

  return (
    <div className="home-container">
      <div className="home-header">
        <h1 className="home-title">Manage Libraries</h1>
        <button 
          onClick={() => setIsCreating(!isCreating)}
          className="btn-create"
        >
          {isCreating ? 'Cancel' : 'Create Library'}
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="create-library-form panel" style={{ backgroundColor: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '8px' }}>
          <h2>Create New Library</h2>
          {createError && <div className="error-banner">{createError}</div>}
          <div className="form-row">
            <div className="form-group">
              <label>Library Name</label>
              <input
                type="text"
                required
                value={newName}
                onChange={e => setNewName(e.target.value)}
                placeholder="e.g. Movies 2025-2026"
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Telegram Channel</label>
              <input
                type="text"
                required
                value={newChannel}
                onChange={e => setNewChannel(e.target.value)}
                placeholder="e.g. -1001234567890 or @channelname"
                className="form-input"
              />
            </div>
          </div>
          <button type="submit" className="btn-submit" style={{ backgroundColor: 'var(--accent-purple)' }}>
            Save Library
          </button>
        </form>
      )}

      <div className="libraries-grid">
        {libraries.map(lib => (
          <Link 
            key={lib.id} 
            to={`/admin/libraries/${lib.slug}`}
            className="library-card"
          >
            <div className="library-card-header" style={{ background: 'linear-gradient(135deg, #1a103c 0%, #0d1117 100%)' }}>
              <h2 style={{ color: 'var(--accent-teal)' }}>{lib.name}</h2>
            </div>
            <div className="library-card-body">
              <p>
                <strong>Channel:</strong> {lib.telegram_channel}
              </p>
              <p>
                <strong>Status:</strong> {lib.is_active ? <span style={{color: 'var(--accent-teal)'}}>Active</span> : <span style={{color: '#ff6b6b'}}>Disabled</span>}
              </p>
              <p>
                <strong>Last Scanned:</strong> {lib.last_scan ? new Date(lib.last_scan).toLocaleString() : 'Never'}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
