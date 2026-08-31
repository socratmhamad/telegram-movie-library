import { useState, useEffect, useCallback, useRef } from 'react';
import {
  adminFetchLibraries,
  adminCreateLibrary,
  adminUpdateLibrary,
  adminReorderLibraries,
  adminDeleteLibrary,
  adminScanLibrary,
  adminUpdateTmdb,
  adminMigrateLibrary,
  adminMigrateTVLibrary,
  adminFetchTasks,
  adminFetchTaskLogs,
  adminCancelTask,
  adminFetchTVLibraries,
  adminCreateTVLibrary,
  adminUpdateTVLibrary,
  adminReorderTVLibraries,
  adminDeleteTVLibrary,
  adminScanTVLibrary,
  adminUpdateTVTmdb,
  adminFetchFeaturedTVSeries,
  adminCreateFeaturedTVSeries,
  adminUpdateFeaturedTVSeries,
  adminDeleteFeaturedTVSeries,
  adminUploadImage,
  formatImageUrl,
} from '../api/client';
import { translateLibraryName } from '../utils/translator';
import AdminAnalytics from './AdminAnalytics';

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function LibraryForm({ library, onSave, onCancel }) {
  const isEdit = !!library;
  const [form, setForm] = useState({
    name: library?.name || '',
    name_en: library?.name_en || '',
    slug: library?.slug || '',
    telegram_channel: library?.telegram_channel || '',
    telegram_channel_id: library?.telegram_channel_id || '',
    is_active: library?.is_active ?? true,
    display_order: library?.display_order ?? '',
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { ...form };
      if (!payload.telegram_channel_id) payload.telegram_channel_id = null;
      if (payload.display_order !== '' && payload.display_order !== null && !isNaN(payload.display_order)) {
        payload.display_order = parseInt(payload.display_order, 10);
      } else {
        delete payload.display_order;
      }
      if (isEdit) {
        await adminUpdateLibrary(library.id, payload);
      } else {
        await adminCreateLibrary(payload);
      }
      onSave();
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="admin-modal-overlay" onClick={onCancel}>
      <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
        <h3>{isEdit ? 'Edit Movie Library' : 'Create Movie Library'}</h3>
        <form onSubmit={handleSubmit} className="admin-form">
          <label>
            <span>Arabic Name</span>
            <input name="name" value={form.name} onChange={handleChange} required />
          </label>
          <label>
            <span>English Name (Optional)</span>
            <input name="name_en" value={form.name_en} onChange={handleChange} />
          </label>
          <label>
            <span>Slug</span>
            <input name="slug" value={form.slug} onChange={handleChange} required />
          </label>
          <label>
            <span>Telegram Channel</span>
            <input name="telegram_channel" value={form.telegram_channel} onChange={handleChange} required placeholder="@channel or https://t.me/+invite" />
          </label>
          <label>
            <span>Channel ID (numeric, optional)</span>
            <input name="telegram_channel_id" value={form.telegram_channel_id} onChange={handleChange} placeholder="e.g. 1234567890" />
          </label>
          <label>
            <span>Display Order (Optional)</span>
            <input
              type="number"
              name="display_order"
              value={form.display_order}
              onChange={handleChange}
              min="0"
              placeholder="e.g. 1 (auto-assigned if blank)"
            />
          </label>
          <label className="admin-checkbox-label">
            <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} />
            <span>Active</span>
          </label>
          <div className="admin-form-actions">
            <button type="submit" className="admin-btn admin-btn-primary" disabled={saving}>
              {saving ? 'Saving...' : (isEdit ? 'Update' : 'Create')}
            </button>
            <button type="button" className="admin-btn admin-btn-secondary" onClick={onCancel}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}


function TVLibraryForm({ library, onSave, onCancel }) {
  const isEdit = !!library;
  const [form, setForm] = useState({
    name: library?.name || '',
    name_en: library?.name_en || '',
    slug: library?.slug || '',
    telegram_channel: library?.telegram_channel || '',
    telegram_channel_id: library?.telegram_channel_id || '',
    is_active: library?.is_active ?? true,
    display_order: library?.display_order ?? '',
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { ...form };
      if (!payload.telegram_channel_id) payload.telegram_channel_id = null;
      if (payload.display_order !== '' && payload.display_order !== null && !isNaN(payload.display_order)) {
        payload.display_order = parseInt(payload.display_order, 10);
      } else {
        delete payload.display_order;
      }
      if (isEdit) {
        await adminUpdateTVLibrary(library.id, payload);
      } else {
        await adminCreateTVLibrary(payload);
      }
      onSave();
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="admin-modal-overlay" onClick={onCancel}>
      <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
        <h3>{isEdit ? 'Edit TV Series Library' : 'Create TV Series Library'}</h3>
        <form onSubmit={handleSubmit} className="admin-form">
          <label>
            <span>Arabic Name</span>
            <input name="name" value={form.name} onChange={handleChange} required />
          </label>
          <label>
            <span>English Name (Optional)</span>
            <input name="name_en" value={form.name_en} onChange={handleChange} />
          </label>
          <label>
            <span>Slug</span>
            <input name="slug" value={form.slug} onChange={handleChange} required />
          </label>
          <label>
            <span>Telegram Channel</span>
            <input name="telegram_channel" value={form.telegram_channel} onChange={handleChange} required placeholder="@channel or https://t.me/+invite" />
          </label>
          <label>
            <span>Channel ID (numeric, optional)</span>
            <input name="telegram_channel_id" value={form.telegram_channel_id} onChange={handleChange} placeholder="e.g. 1234567890" />
          </label>
          <label>
            <span>Display Order (Optional)</span>
            <input
              type="number"
              name="display_order"
              value={form.display_order}
              onChange={handleChange}
              min="0"
              placeholder="e.g. 1 (auto-assigned if blank)"
            />
          </label>
          <label className="admin-checkbox-label">
            <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} />
            <span>Active</span>
          </label>
          <div className="admin-form-actions">
            <button type="submit" className="admin-btn admin-btn-primary" disabled={saving}>
              {saving ? 'Saving...' : (isEdit ? 'Update' : 'Create')}
            </button>
            <button type="button" className="admin-btn admin-btn-secondary" onClick={onCancel}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}


function MigrateForm({ library, isTV = false, onClose }) {
  const [form, setForm] = useState({
    new_channel: '',
    new_channel_id: '',
    dry_run: true,
  });
  const [launching, setLaunching] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLaunching(true);
    try {
      const payload = { ...form };
      if (!payload.new_channel_id) payload.new_channel_id = null;
      if (isTV) {
        await adminMigrateTVLibrary(library.id, payload);
      } else {
        await adminMigrateLibrary(library.id, payload);
      }
      onClose('launched');
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setLaunching(false);
    }
  };

  return (
    <div className="admin-modal-overlay" onClick={onClose}>
      <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
        <h3>Migrate Channel — {library.name} {isTV ? '(TV Series)' : ''}</h3>
        <p className="admin-migrate-info">
          Current channel: <code>{library.telegram_channel}</code>
        </p>
        <form onSubmit={handleSubmit} className="admin-form">
          <label>
            <span>New Channel URL / Handle</span>
            <input name="new_channel" value={form.new_channel} onChange={handleChange} required placeholder="@new_channel or https://t.me/+invite" />
          </label>
          <label>
            <span>New Channel ID (numeric, for private channels)</span>
            <input name="new_channel_id" value={form.new_channel_id} onChange={handleChange} placeholder="e.g. 9876543210" />
          </label>
          <label className="admin-checkbox-label">
            <input type="checkbox" name="dry_run" checked={form.dry_run} onChange={handleChange} />
            <span>Dry Run (preview only, no DB changes)</span>
          </label>
          <div className="admin-form-actions">
            <button type="submit" className="admin-btn admin-btn-warning" disabled={launching}>
              {launching ? 'Launching...' : (form.dry_run ? '🔍 Preview Migration' : '⚡ Execute Migration')}
            </button>
            <button type="button" className="admin-btn admin-btn-secondary" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}


function FeaturedTVForm({ item, onSave, onCancel }) {
  const isEdit = !!item;
  const [form, setForm] = useState({
    title: item?.title || '',
    poster_url: item?.poster_url || '',
    telegram_channel_link: item?.telegram_channel_link || '',
    description: item?.description || '',
    category: item?.category || 'Trending',
  });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await adminUploadImage(formData);
      if (res && res.url) {
        setForm((f) => ({ ...f, poster_url: res.url }));
      }
    } catch (err) {
      alert('Image upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (isEdit) {
        await adminUpdateFeaturedTVSeries(item.id, form);
      } else {
        await adminCreateFeaturedTVSeries(form);
      }
      onSave();
    } catch (err) {
      alert('Error saving featured series: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="admin-modal-overlay" onClick={onCancel}>
      <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
        <h3>{isEdit ? 'Edit Featured TV Series' : 'New Featured TV Series'}</h3>
        <form onSubmit={handleSubmit} className="admin-form">
          <label>
            <span>Title</span>
            <input name="title" value={form.title} onChange={handleChange} required placeholder="e.g. Breaking Bad" />
          </label>

          <label>
            <span>Category Tag</span>
            <select name="category" value={form.category} onChange={handleChange}>
              <option value="Trending">Trending (شائع)</option>
              <option value="Popular">Popular (الأكثر مشاهدة)</option>
              <option value="Currently Airing">Currently Airing (يعرض حالياً)</option>
            </select>
          </label>

          <label>
            <span>Poster Image (Upload File or Enter URL)</span>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <input
                name="poster_url"
                value={form.poster_url}
                onChange={handleChange}
                required
                placeholder="Image URL or upload file..."
                style={{ flex: 1 }}
              />
              <label className="admin-btn admin-btn-sm admin-btn-secondary" style={{ cursor: 'pointer', margin: 0, whiteSpace: 'nowrap' }}>
                {uploading ? 'Uploading...' : '📁 Upload Image'}
                <input type="file" accept="image/*" onChange={handleFileUpload} style={{ display: 'none' }} disabled={uploading} />
              </label>
            </div>
          </label>

          {form.poster_url && (
            <div style={{ margin: '0.5rem 0', textAlign: 'center' }}>
              <img
                src={formatImageUrl(form.poster_url)}
                alt="Poster preview"
                style={{ maxHeight: '120px', borderRadius: '6px', border: '1px solid var(--bg-glass-border)', objectFit: 'cover' }}
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            </div>
          )}

          <label>
            <span>Telegram Channel / Message Link</span>
            <input name="telegram_channel_link" value={form.telegram_channel_link} onChange={handleChange} required placeholder="https://t.me/c/12345678/100 or @channel" />
          </label>

          <label>
            <span>Short Description (Optional)</span>
            <textarea name="description" value={form.description} onChange={handleChange} rows={3} placeholder="Brief summary or description..." />
          </label>

          <div className="admin-form-actions">
            <button type="submit" className="admin-btn admin-btn-primary" disabled={saving || uploading}>
              {saving ? 'Saving...' : (isEdit ? 'Update Series' : 'Create Series')}
            </button>
            <button type="button" className="admin-btn admin-btn-secondary" onClick={onCancel}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}


function TaskLogViewer({ taskId, onClose }) {
  const [logs, setLogs] = useState('Loading...');
  const [status, setStatus] = useState('');
  const logRef = useRef(null);
  const intervalRef = useRef(null);

  const fetchLogs = useCallback(async () => {
    try {
      const data = await adminFetchTaskLogs(taskId);
      setLogs(data.logs || '(no output yet)');
      if (logRef.current) {
        logRef.current.scrollTop = logRef.current.scrollHeight;
      }
    } catch (err) {
      setLogs('Error loading logs: ' + err.message);
    }
  }, [taskId]);

  useEffect(() => {
    fetchLogs();
    intervalRef.current = setInterval(fetchLogs, 2000);
    return () => clearInterval(intervalRef.current);
  }, [fetchLogs]);

  const handleCancel = async () => {
    try {
      await adminCancelTask(taskId);
      setStatus('Cancelled');
    } catch (err) {
      alert('Error cancelling: ' + err.message);
    }
  };

  return (
    <div className="admin-modal-overlay" onClick={onClose}>
      <div className="admin-modal admin-modal-wide" onClick={(e) => e.stopPropagation()}>
        <div className="admin-log-header">
          <h3>Task Logs — <code>{taskId}</code></h3>
          <div className="admin-log-actions">
            <button className="admin-btn admin-btn-secondary admin-btn-sm" onClick={fetchLogs}>↻ Refresh</button>
            <button className="admin-btn admin-btn-danger admin-btn-sm" onClick={handleCancel}>Cancel Task</button>
            <button className="admin-btn admin-btn-secondary admin-btn-sm" onClick={onClose}>Close</button>
          </div>
        </div>
        {status && <p className="admin-status-msg">{status}</p>}
        <pre className="admin-log-console" ref={logRef}>{logs}</pre>
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Main Dashboard
// ---------------------------------------------------------------------------

export default function AdminDashboard({ onBack, onLogout, lang = 'en' }) {
  const [libraries, setLibraries] = useState([]);
  const [tvLibraries, setTvLibraries] = useState([]);
  const [featuredTV, setFeaturedTV] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editLib, setEditLib] = useState(null);        // null | 'new' | library object
  const [editTVLib, setEditTVLib] = useState(null);    // null | 'new' | library object
  const [editFeaturedTV, setEditFeaturedTV] = useState(null); // null | 'new' | item
  const [migrateLib, setMigrateLib] = useState(null);   // null | library object
  const [viewLogs, setViewLogs] = useState(null);       // null | task_id
  const [activeTab, setActiveTab] = useState('libraries');
  const [draggedIndex, setDraggedIndex] = useState(null);
  const [dragOverIndex, setDragOverIndex] = useState(null);
  const [dragType, setDragType] = useState(null);
  const [reorderSaving, setReorderSaving] = useState(false);
  const [orderNotification, setOrderNotification] = useState(null);

  const isAr = lang === 'ar';

  const showOrderSavedNotification = (msg) => {
    setOrderNotification(msg);
    setTimeout(() => {
      setOrderNotification((prev) => (prev === msg ? null : prev));
    }, 2500);
  };

  const handleMoveLib = async (index, direction, isTV = false) => {
    const list = isTV ? [...tvLibraries] : [...libraries];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= list.length) return;

    const temp = list[index];
    list[index] = list[targetIndex];
    list[targetIndex] = temp;

    if (isTV) {
      setTvLibraries(list);
    } else {
      setLibraries(list);
    }

    setReorderSaving(true);
    try {
      const ids = list.map((l) => l.id);
      if (isTV) {
        await adminReorderTVLibraries(ids);
      } else {
        await adminReorderLibraries(ids);
      }
      showOrderSavedNotification(isAr ? 'تم حفظ الترتيب بنجاح ✓' : 'Library order saved ✓');
    } catch (err) {
      alert('Failed to save order: ' + err.message);
      refreshData();
    } finally {
      setReorderSaving(false);
    }
  };

  const handleDragStart = (e, index, type) => {
    setDraggedIndex(index);
    setDragType(type);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', index.toString());
  };

  const handleDragOver = (e, index, type) => {
    if (dragType !== type) return;
    e.preventDefault();
    if (dragOverIndex !== index) {
      setDragOverIndex(index);
    }
  };

  const handleDrop = async (e, dropIndex, isTV = false) => {
    const type = isTV ? 'tv' : 'movie';
    if (dragType !== type) return;
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDraggedIndex(null);
      setDragOverIndex(null);
      setDragType(null);
      return;
    }

    const list = isTV ? [...tvLibraries] : [...libraries];
    const [movedItem] = list.splice(draggedIndex, 1);
    list.splice(dropIndex, 0, movedItem);

    if (isTV) {
      setTvLibraries(list);
    } else {
      setLibraries(list);
    }

    setDraggedIndex(null);
    setDragOverIndex(null);
    setDragType(null);

    setReorderSaving(true);
    try {
      const ids = list.map((l) => l.id);
      if (isTV) {
        await adminReorderTVLibraries(ids);
      } else {
        await adminReorderLibraries(ids);
      }
      showOrderSavedNotification(isAr ? 'تم حفظ الترتيب بنجاح ✓' : 'Library order saved ✓');
    } catch (err) {
      alert('Failed to save order: ' + err.message);
      refreshData();
    } finally {
      setReorderSaving(false);
    }
  };

  const refreshData = useCallback(async () => {
    try {
      const [libs, tvLibs, taskData, featuredData] = await Promise.all([
        adminFetchLibraries(),
        adminFetchTVLibraries(),
        adminFetchTasks(),
        adminFetchFeaturedTVSeries().catch(() => ({ items: [] })),
      ]);
      setLibraries(Array.isArray(libs) ? libs : []);
      setTvLibraries(Array.isArray(tvLibs) ? tvLibs : []);
      setTasks(taskData?.tasks || []);
      setFeaturedTV(featuredData?.items || []);
    } catch (err) {
      console.error('Admin refresh error:', err);
      if (err.message?.includes('401') || err.message?.includes('Unauthorized')) {
        if (onLogout) onLogout();
      }
    } finally {
      setLoading(false);
    }
  }, [onLogout]);

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 5000);
    return () => clearInterval(interval);
  }, [refreshData]);

  const handleDeleteLib = async (lib) => {
    if (!confirm(`Delete movie library "${lib.name}" and all its ${lib.movie_count} movies? This cannot be undone.`)) return;
    try {
      await adminDeleteLibrary(lib.id);
      refreshData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleDeleteTVLib = async (lib) => {
    if (!confirm(`Delete TV library "${lib.name}" and all its ${lib.series_count} series? This cannot be undone.`)) return;
    try {
      await adminDeleteTVLibrary(lib.id);
      refreshData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleDeleteFeaturedTV = async (item) => {
    if (!confirm(`Delete featured TV series "${item.title}"? This cannot be undone.`)) return;
    try {
      await adminDeleteFeaturedTVSeries(item.id);
      refreshData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleToggleActive = async (lib, isTV = false) => {
    try {
      const nextActive = !lib.is_active;
      if (isTV) {
        await adminUpdateTVLibrary(lib.id, { is_active: nextActive });
      } else {
        await adminUpdateLibrary(lib.id, { is_active: nextActive });
      }
      refreshData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleScan = async (lib) => {
    try {
      await adminScanLibrary(lib.id);
      setActiveTab('tasks');
      refreshData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleTVScan = async (lib) => {
    try {
      await adminScanTVLibrary(lib.id);
      setActiveTab('tasks');
      refreshData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleTmdb = async (lib) => {
    try {
      await adminUpdateTmdb(lib.id);
      setActiveTab('tasks');
      refreshData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleTVTmdb = async (lib) => {
    try {
      await adminUpdateTVTmdb(lib.id);
      setActiveTab('tasks');
      refreshData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const statusBadge = (status) => {
    const cls = {
      running: 'admin-badge-running',
      completed: 'admin-badge-completed',
      failed: 'admin-badge-failed',
      cancelled: 'admin-badge-cancelled',
      pending: 'admin-badge-pending',
    }[status] || '';
    return <span className={`admin-badge ${cls}`}>{status}</span>;
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="loading-spinner"><div className="spinner" /></div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
        <div className="admin-header-left" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-start' }}>
          <button className="library-back-btn" onClick={onBack}>
            <span className="arrow">{isAr ? '←' : '←'}</span>
            <span className="text">{isAr ? 'العودة للمكتبات' : 'Back to Libraries'}</span>
          </button>
          <h1 className="admin-title">{isAr ? 'لوحة الإدارة' : 'Admin Dashboard'}</h1>
        </div>
        {onLogout && (
          <button 
            className="admin-btn admin-btn-danger" 
            onClick={onLogout} 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem', 
              padding: '0.6rem 1.2rem',
              fontSize: '0.9rem',
              fontWeight: 500,
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            <span>🚪</span>
            <span>{isAr ? 'تسجيل الخروج' : 'Logout'}</span>
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        <button className={`admin-tab ${activeTab === 'libraries' ? 'active' : ''}`} onClick={() => setActiveTab('libraries')}>
          📚 Movie Libraries
        </button>
        <button className={`admin-tab ${activeTab === 'tv-libraries' ? 'active' : ''}`} onClick={() => setActiveTab('tv-libraries')}>
          📺 TV Libraries {tvLibraries.length > 0 && (
            <span className="admin-badge admin-badge-info">{tvLibraries.length}</span>
          )}
        </button>
        <button className={`admin-tab ${activeTab === 'featured-tv' ? 'active' : ''}`} onClick={() => setActiveTab('featured-tv')}>
          🌟 Featured TV {featuredTV.length > 0 && (
            <span className="admin-badge admin-badge-info">{featuredTV.length}</span>
          )}
        </button>
        <button className={`admin-tab ${activeTab === 'tasks' ? 'active' : ''}`} onClick={() => setActiveTab('tasks')}>
          ⚙️ Tasks {tasks.filter(t => t.status === 'running').length > 0 && (
            <span className="admin-badge admin-badge-running">{tasks.filter(t => t.status === 'running').length}</span>
          )}
        </button>
        <button className={`admin-tab ${activeTab === 'analytics' ? 'active' : ''}`} onClick={() => setActiveTab('analytics')}>
          📊 Analytics
        </button>
      </div>

      {/* Movie Libraries Tab */}
      {activeTab === 'libraries' && (
        <div className="admin-section">
          <div className="admin-section-header">
            <div className="admin-section-title-wrap">
              <h2>Movie Libraries</h2>
              <span className="admin-section-hint">
                {isAr ? 'اسحب الصفوف أو استخدم ▲ / ▼ لضبط ترتيب العرض للمستخدمين' : 'Drag rows (⠿) or click ▲ / ▼ to reorder libraries'}
              </span>
            </div>
            <div className="admin-header-actions" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {reorderSaving && <span className="admin-saving-tag">⏳ {isAr ? 'جاري حفظ الترتيب...' : 'Saving order...'}</span>}
              {orderNotification && <span className="admin-order-notification">✨ {orderNotification}</span>}
              <button className="admin-btn admin-btn-primary" onClick={() => setEditLib('new')}>+ New Movie Library</button>
            </div>
          </div>

          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th style={{ width: '90px' }}>{isAr ? 'الترتيب' : 'Order'}</th>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Slug</th>
                  <th>Channel</th>
                  <th>Movies</th>
                  <th>TMDB</th>
                  <th>Messages</th>
                  <th>Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {libraries.map((lib, idx) => (
                  <tr
                    key={lib.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, idx, 'movie')}
                    onDragOver={(e) => handleDragOver(e, idx, 'movie')}
                    onDrop={(e) => handleDrop(e, idx, false)}
                    onDragEnd={() => { setDraggedIndex(null); setDragOverIndex(null); setDragType(null); }}
                    className={`admin-draggable-row ${dragType === 'movie' && draggedIndex === idx ? 'is-dragging' : ''} ${dragType === 'movie' && dragOverIndex === idx ? 'drag-over' : ''}`}
                  >
                    <td className="admin-cell-order">
                      <div className="admin-order-controls">
                        <span className="admin-drag-handle" title="Drag to reorder">⠿</span>
                        <span className="admin-order-badge">#{idx + 1}</span>
                        <div className="admin-reorder-btns">
                          <button
                            type="button"
                            className="admin-order-btn"
                            disabled={idx === 0}
                            onClick={() => handleMoveLib(idx, -1, false)}
                            title="Move Up"
                          >
                            ▲
                          </button>
                          <button
                            type="button"
                            className="admin-order-btn"
                            disabled={idx === libraries.length - 1}
                            onClick={() => handleMoveLib(idx, 1, false)}
                            title="Move Down"
                          >
                            ▼
                          </button>
                        </div>
                      </div>
                    </td>
                    <td className="admin-cell-id">{lib.id}</td>
                    <td className="admin-cell-name">{translateLibraryName(lib.name, lang)}</td>
                    <td><code>{lib.slug}</code></td>
                    <td className="admin-cell-channel" title={lib.telegram_channel}>
                      {lib.telegram_channel?.length > 30 ? lib.telegram_channel.slice(0, 30) + '…' : lib.telegram_channel}
                    </td>
                    <td className="admin-cell-num">{lib.movie_count}</td>
                    <td className="admin-cell-num">
                      <span className="admin-tmdb-stat">
                        {lib.movies_with_tmdb}
                        <span className="admin-tmdb-pct">
                          ({lib.movie_count > 0 ? Math.round(lib.movies_with_tmdb / lib.movie_count * 100) : 0}%)
                        </span>
                      </span>
                    </td>
                    <td className="admin-cell-num">{lib.total_messages}</td>
                    <td>
                      <button
                        className={`admin-toggle-btn ${lib.is_active ? 'enabled' : 'disabled'}`}
                        onClick={() => handleToggleActive(lib, false)}
                        title={lib.is_active ? 'Click to Disable' : 'Click to Enable'}
                      >
                        {lib.is_active ? '🟢 Enabled' : '🔴 Disabled'}
                      </button>
                    </td>
                    <td className="admin-cell-actions">
                      <button className="admin-btn admin-btn-sm admin-btn-secondary" onClick={() => setEditLib(lib)} title="Edit">✏️</button>
                      <button className="admin-btn admin-btn-sm admin-btn-primary" onClick={() => handleScan(lib)} title="Scan channel">📡</button>
                      <button className="admin-btn admin-btn-sm admin-btn-accent" onClick={() => handleTmdb(lib)} title="TMDB update">🎬</button>
                      <button className="admin-btn admin-btn-sm admin-btn-warning" onClick={() => setMigrateLib({ library: lib, isTV: false })} title="Migrate channel">🔄</button>
                      <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => handleDeleteLib(lib)} title="Delete">🗑️</button>
                    </td>
                  </tr>
                ))}
                {libraries.length === 0 && (
                  <tr><td colSpan="10" className="admin-empty">No movie libraries found. Create one to get started.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TV Series Libraries Tab */}
      {activeTab === 'tv-libraries' && (
        <div className="admin-section">
          <div className="admin-section-header">
            <div className="admin-section-title-wrap">
              <h2>TV Series Libraries</h2>
              <span className="admin-section-hint">
                {isAr ? 'اسحب الصفوف أو استخدم ▲ / ▼ لضبط ترتيب العرض للمستخدمين' : 'Drag rows (⠿) or click ▲ / ▼ to reorder libraries'}
              </span>
            </div>
            <div className="admin-header-actions" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {reorderSaving && <span className="admin-saving-tag">⏳ {isAr ? 'جاري حفظ الترتيب...' : 'Saving order...'}</span>}
              {orderNotification && <span className="admin-order-notification">✨ {orderNotification}</span>}
              <button className="admin-btn admin-btn-primary" onClick={() => setEditTVLib('new')}>+ New TV Library</button>
            </div>
          </div>

          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th style={{ width: '90px' }}>{isAr ? 'الترتيب' : 'Order'}</th>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Slug</th>
                  <th>Channel</th>
                  <th>Series</th>
                  <th>TMDB</th>
                  <th>Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tvLibraries.map((lib, idx) => (
                  <tr
                    key={lib.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, idx, 'tv')}
                    onDragOver={(e) => handleDragOver(e, idx, 'tv')}
                    onDrop={(e) => handleDrop(e, idx, true)}
                    onDragEnd={() => { setDraggedIndex(null); setDragOverIndex(null); setDragType(null); }}
                    className={`admin-draggable-row ${dragType === 'tv' && draggedIndex === idx ? 'is-dragging' : ''} ${dragType === 'tv' && dragOverIndex === idx ? 'drag-over' : ''}`}
                  >
                    <td className="admin-cell-order">
                      <div className="admin-order-controls">
                        <span className="admin-drag-handle" title="Drag to reorder">⠿</span>
                        <span className="admin-order-badge">#{idx + 1}</span>
                        <div className="admin-reorder-btns">
                          <button
                            type="button"
                            className="admin-order-btn"
                            disabled={idx === 0}
                            onClick={() => handleMoveLib(idx, -1, true)}
                            title="Move Up"
                          >
                            ▲
                          </button>
                          <button
                            type="button"
                            className="admin-order-btn"
                            disabled={idx === tvLibraries.length - 1}
                            onClick={() => handleMoveLib(idx, 1, true)}
                            title="Move Down"
                          >
                            ▼
                          </button>
                        </div>
                      </div>
                    </td>
                    <td className="admin-cell-id">{lib.id}</td>
                    <td className="admin-cell-name">{translateLibraryName(lib.name, lang)}</td>
                    <td><code>{lib.slug}</code></td>
                    <td className="admin-cell-channel" title={lib.telegram_channel}>
                      {lib.telegram_channel?.length > 30 ? lib.telegram_channel.slice(0, 30) + '…' : lib.telegram_channel}
                    </td>
                    <td className="admin-cell-num">{lib.series_count}</td>
                    <td className="admin-cell-num">
                      <span className="admin-tmdb-stat">
                        {lib.series_with_tmdb}
                        <span className="admin-tmdb-pct">
                          ({lib.series_count > 0 ? Math.round(lib.series_with_tmdb / lib.series_count * 100) : 0}%)
                        </span>
                      </span>
                    </td>
                    <td>
                      <button
                        className={`admin-toggle-btn ${lib.is_active ? 'enabled' : 'disabled'}`}
                        onClick={() => handleToggleActive(lib, true)}
                        title={lib.is_active ? 'Click to Disable' : 'Click to Enable'}
                      >
                        {lib.is_active ? '🟢 Enabled' : '🔴 Disabled'}
                      </button>
                    </td>
                    <td className="admin-cell-actions">
                      <button className="admin-btn admin-btn-sm admin-btn-secondary" onClick={() => setEditTVLib(lib)} title="Edit">✏️</button>
                      <button className="admin-btn admin-btn-sm admin-btn-primary" onClick={() => handleTVScan(lib)} title="Scan channel">📡</button>
                      <button className="admin-btn admin-btn-sm admin-btn-accent" onClick={() => handleTVTmdb(lib)} title="TMDB update">🎬</button>
                      <button className="admin-btn admin-btn-sm admin-btn-warning" onClick={() => setMigrateLib({ library: lib, isTV: true })} title="Migrate channel">🔄</button>
                      <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => handleDeleteTVLib(lib)} title="Delete">🗑️</button>
                    </td>
                  </tr>
                ))}
                {tvLibraries.length === 0 && (
                  <tr><td colSpan="9" className="admin-empty">No TV series libraries found. Create one to get started.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tasks Tab */}
      {activeTab === 'tasks' && (
        <div className="admin-section">
          <div className="admin-section-header">
            <h2>Background Tasks</h2>
            <button className="admin-btn admin-btn-secondary" onClick={refreshData}>↻ Refresh</button>
          </div>

          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Task ID</th>
                  <th>Type</th>
                  <th>Library</th>
                  <th>Status</th>
                  <th>Description</th>
                  <th>Duration</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => {
                  const duration = task.finished_at
                    ? ((task.finished_at - task.started_at) || 0).toFixed(1) + 's'
                    : task.started_at
                      ? ((Date.now() / 1000 - task.started_at) || 0).toFixed(0) + 's…'
                      : '—';
                  return (
                    <tr key={task.id}>
                      <td><code className="admin-task-id">{task.id}</code></td>
                      <td>{task.task_type}</td>
                      <td className="admin-cell-num">{task.library_id}</td>
                      <td>{statusBadge(task.status)}</td>
                      <td className="admin-cell-desc">{task.description}</td>
                      <td className="admin-cell-num">{duration}</td>
                      <td className="admin-cell-actions">
                        <button className="admin-btn admin-btn-sm admin-btn-secondary" onClick={() => setViewLogs(task.id)} title="View logs">📋</button>
                        {task.status === 'running' && (
                          <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={async () => { await adminCancelTask(task.id); refreshData(); }} title="Cancel">✕</button>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {tasks.length === 0 && (
                  <tr><td colSpan="7" className="admin-empty">No tasks yet. Launch a scan or update from the Libraries tab.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Featured TV Series Tab */}
      {activeTab === 'featured-tv' && (
        <div className="admin-section">
          <div className="admin-section-header">
            <h2>Featured & Trending TV Series</h2>
            <button className="admin-btn admin-btn-primary" onClick={() => setEditFeaturedTV('new')}>+ New Featured Series</button>
          </div>

          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Poster</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Telegram Link</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {featuredTV.map((item) => (
                  <tr key={item.id}>
                    <td className="admin-cell-id">{item.id}</td>
                    <td>
                      {item.poster_url ? (
                        <img src={formatImageUrl(item.poster_url)} alt="" style={{ width: '45px', height: '65px', objectFit: 'cover', borderRadius: '4px' }} />
                      ) : (
                        <span style={{ fontSize: '1.5rem' }}>📺</span>
                      )}
                    </td>
                    <td className="admin-cell-name">{translateLibraryName(item.title, lang)}</td>
                    <td><span className="admin-badge admin-badge-info">{item.category}</span></td>
                    <td className="admin-cell-channel" title={item.telegram_channel_link}>
                      {item.telegram_channel_link?.length > 30 ? item.telegram_channel_link.slice(0, 30) + '…' : item.telegram_channel_link}
                    </td>
                    <td className="admin-cell-desc" style={{ maxWidth: '250px' }}>{item.description || '—'}</td>
                    <td className="admin-cell-actions">
                      <button className="admin-btn admin-btn-sm admin-btn-secondary" onClick={() => setEditFeaturedTV(item)} title="Edit">✏️</button>
                      <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => handleDeleteFeaturedTV(item)} title="Delete">🗑️</button>
                    </td>
                  </tr>
                ))}
                {featuredTV.length === 0 && (
                  <tr><td colSpan="7" className="admin-empty">No featured TV series found. Add one to display it on the main page.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modals */}
      {editLib && (
        <LibraryForm
          library={editLib === 'new' ? null : editLib}
          onSave={() => { setEditLib(null); refreshData(); }}
          onCancel={() => setEditLib(null)}
        />
      )}
      {editTVLib && (
        <TVLibraryForm
          library={editTVLib === 'new' ? null : editTVLib}
          onSave={() => { setEditTVLib(null); refreshData(); }}
          onCancel={() => setEditTVLib(null)}
        />
      )}
      {editFeaturedTV && (
        <FeaturedTVForm
          item={editFeaturedTV === 'new' ? null : editFeaturedTV}
          onSave={() => { setEditFeaturedTV(null); refreshData(); }}
          onCancel={() => setEditFeaturedTV(null)}
        />
      )}
      {migrateLib && (
        <MigrateForm
          library={migrateLib.library}
          isTV={migrateLib.isTV}
          onClose={(result) => { setMigrateLib(null); if (result) { setActiveTab('tasks'); refreshData(); } }}
        />
      )}
      {viewLogs && (
        <TaskLogViewer
          taskId={viewLogs}
          onClose={() => setViewLogs(null)}
        />
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="admin-section">
          <AdminAnalytics lang={lang} />
        </div>
      )}
    </div>
  );
}
