import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { fetchLibrary, updateLibrary } from '../api/client';

export default function LibrarySettings() {
  const { librarySlug } = useParams();
  const navigate = useNavigate();
  
  const [library, setLibrary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    telegram_channel: '',
    telegram_channel_id: '',
    is_active: true
  });
  
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadLibrary();
  }, [librarySlug]);

  const loadLibrary = async () => {
    try {
      setLoading(true);
      const data = await fetchLibrary(librarySlug);
      setLibrary(data);
      setFormData({
        name: data.name,
        slug: data.slug,
        telegram_channel: data.telegram_channel,
        telegram_channel_id: data.telegram_channel_id || '',
        is_active: data.is_active
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setSuccess(false);
    setSaveError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveError(null);
    setSuccess(false);
    
    try {
      const updated = await updateLibrary(librarySlug, formData);
      setSuccess(true);
      if (updated.slug !== librarySlug) {
        // Slug changed, navigate to new URL
        navigate(`/admin/libraries/${updated.slug}/settings`, { replace: true });
      } else {
        setLibrary(updated);
      }
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Loading settings...</div>;
  if (error) return <div className="error-banner">{error}</div>;
  if (!library) return <div>Library not found</div>;

  return (
    <div className="home-container" style={{ maxWidth: '800px' }}>
      <div className="home-header">
        <h1 className="home-title">Library Settings</h1>
        <Link to={`/admin/libraries/${librarySlug}`} className="btn-create" style={{ backgroundColor: 'var(--text-muted)' }}>
          ← Back to Administration
        </Link>
      </div>

      <div className="panel" style={{ backgroundColor: 'var(--bg-secondary)', padding: '2rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
        {saveError && <div className="error-banner">{saveError}</div>}
        {success && <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(45,212,191,0.1)', color: 'var(--accent-teal)', borderRadius: '4px' }}>Settings saved successfully!</div>}
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          <div className="form-group">
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Library Name</label>
            <input 
              type="text" 
              name="name" 
              value={formData.name} 
              onChange={handleChange} 
              required 
              className="form-input"
              style={{ width: '100%', maxWidth: '400px' }}
            />
          </div>

          <div className="form-group">
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>URL Slug</label>
            <input 
              type="text" 
              name="slug" 
              value={formData.slug} 
              onChange={handleChange} 
              required 
              className="form-input"
              style={{ width: '100%', maxWidth: '400px', fontFamily: 'monospace' }}
            />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Used in URLs (e.g., /library/your-slug)</p>
          </div>

          <div className="form-group">
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Telegram Channel</label>
            <input 
              type="text" 
              name="telegram_channel" 
              value={formData.telegram_channel} 
              onChange={handleChange} 
              required 
              className="form-input"
              style={{ width: '100%', maxWidth: '400px' }}
            />
          </div>

          <div className="form-group">
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Numeric Channel ID (Optional)</label>
            <input 
              type="text" 
              name="telegram_channel_id" 
              value={formData.telegram_channel_id || ''} 
              onChange={handleChange} 
              className="form-input"
              style={{ width: '100%', maxWidth: '400px' }}
              placeholder="e.g. 1234567890"
            />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Required for t.me/c/ deep links if this is a private channel.</p>
          </div>

          <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <input 
              type="checkbox" 
              name="is_active" 
              id="is_active"
              checked={formData.is_active} 
              onChange={handleChange} 
              style={{ width: '18px', height: '18px' }}
            />
            <label htmlFor="is_active" style={{ color: 'var(--text-primary)', cursor: 'pointer' }}>Library is Active</label>
          </div>

          <div style={{ marginTop: '1rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-subtle)' }}>
            <button 
              type="submit" 
              disabled={saving}
              className="btn-submit"
              style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
