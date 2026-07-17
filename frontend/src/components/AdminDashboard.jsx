import { useState, useEffect, useCallback, useRef } from 'react';
import {
  adminFetchLibraries,
  adminCreateLibrary,
  adminUpdateLibrary,
  adminDeleteLibrary,
  adminScanLibrary,
  adminUpdateTmdb,
  adminMigrateLibrary,
  adminFetchTasks,
  adminFetchTaskLogs,
  adminCancelTask,
} from '../api/client';

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function LibraryForm({ library, onSave, onCancel }) {
  const isEdit = !!library;
  const [form, setForm] = useState({
    name: library?.name || '',
    slug: library?.slug || '',
    telegram_channel: library?.telegram_channel || '',
    telegram_channel_id: library?.telegram_channel_id || '',
    is_active: library?.is_active ?? true,
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
        <h3>{isEdit ? 'Edit Library' : 'Create Library'}</h3>
        <form onSubmit={handleSubmit} className="admin-form">
          <label>
            <span>Name</span>
            <input name="name" value={form.name} onChange={handleChange} required />
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


function MigrateForm({ library, onClose }) {
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
      await adminMigrateLibrary(library.id, payload);
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
        <h3>Migrate Channel — {library.name}</h3>
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


function TaskLogViewer({ taskId, onClose }) {
  const [logs, setLogs] = useState('Loading...');
  const [status, setStatus] = useState('');
  const logRef = useRef(null);
  const intervalRef = useRef(null);

  const fetchLogs = useCallback(async () => {
    try {
      const data = await adminFetchTaskLogs(taskId);
      setLogs(data.logs || '(no output yet)');
      // Auto-scroll
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
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editLib, setEditLib] = useState(null);      // null | 'new' | library object
  const [migrateLib, setMigrateLib] = useState(null); // null | library object
  const [viewLogs, setViewLogs] = useState(null);     // null | task_id
  const [activeTab, setActiveTab] = useState('libraries');

  const refreshData = useCallback(async () => {
    try {
      const [libs, taskData] = await Promise.all([
        adminFetchLibraries(),
        adminFetchTasks(),
      ]);
      setLibraries(Array.isArray(libs) ? libs : []);
      setTasks(taskData?.tasks || []);
    } catch (err) {
      console.error('Admin refresh error:', err);
      if (err.message.includes('401') || err.message.includes('Unauthorized')) {
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
    if (!confirm(`Delete library "${lib.name}" and all its ${lib.movie_count} movies? This cannot be undone.`)) return;
    try {
      await adminDeleteLibrary(lib.id);
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

  const handleTmdb = async (lib) => {
    try {
      await adminUpdateTmdb(lib.id);
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

  const isAr = lang === 'ar';

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
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer',
              border: 'none',
              transition: 'all var(--transition-fast)'
            }}
          >
            {isAr ? '🚪 خروج' : '🚪 Logout'}
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        <button className={`admin-tab ${activeTab === 'libraries' ? 'active' : ''}`} onClick={() => setActiveTab('libraries')}>
          📚 Libraries
        </button>
        <button className={`admin-tab ${activeTab === 'tasks' ? 'active' : ''}`} onClick={() => setActiveTab('tasks')}>
          ⚙️ Tasks {tasks.filter(t => t.status === 'running').length > 0 && (
            <span className="admin-badge admin-badge-running">{tasks.filter(t => t.status === 'running').length}</span>
          )}
        </button>
      </div>

      {/* Libraries Tab */}
      {activeTab === 'libraries' && (
        <div className="admin-section">
          <div className="admin-section-header">
            <h2>Libraries</h2>
            <button className="admin-btn admin-btn-primary" onClick={() => setEditLib('new')}>+ New Library</button>
          </div>

          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
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
                {libraries.map((lib) => (
                  <tr key={lib.id}>
                    <td className="admin-cell-id">{lib.id}</td>
                    <td className="admin-cell-name">{lib.name}</td>
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
                    <td>{lib.is_active ? '✅' : '❌'}</td>
                    <td className="admin-cell-actions">
                      <button className="admin-btn admin-btn-sm admin-btn-secondary" onClick={() => setEditLib(lib)} title="Edit">✏️</button>
                      <button className="admin-btn admin-btn-sm admin-btn-primary" onClick={() => handleScan(lib)} title="Scan channel">📡</button>
                      <button className="admin-btn admin-btn-sm admin-btn-accent" onClick={() => handleTmdb(lib)} title="TMDB update">🎬</button>
                      <button className="admin-btn admin-btn-sm admin-btn-warning" onClick={() => setMigrateLib(lib)} title="Migrate channel">🔄</button>
                      <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => handleDeleteLib(lib)} title="Delete">🗑️</button>
                    </td>
                  </tr>
                ))}
                {libraries.length === 0 && (
                  <tr><td colSpan="9" className="admin-empty">No libraries found. Create one to get started.</td></tr>
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

      {/* Modals */}
      {editLib && (
        <LibraryForm
          library={editLib === 'new' ? null : editLib}
          onSave={() => { setEditLib(null); refreshData(); }}
          onCancel={() => setEditLib(null)}
        />
      )}
      {migrateLib && (
        <MigrateForm
          library={migrateLib}
          onClose={(result) => { setMigrateLib(null); if (result) { setActiveTab('tasks'); refreshData(); } }}
        />
      )}
      {viewLogs && (
        <TaskLogViewer
          taskId={viewLogs}
          onClose={() => setViewLogs(null)}
        />
      )}
    </div>
  );
}
