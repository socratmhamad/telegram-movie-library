import { useState } from 'react';
import { login } from '../api/adminAuth';

export default function AdminLogin({ onLoginSuccess, onBack, lang = 'en' }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isAr = lang === 'ar';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(username, password);
      onLoginSuccess();
    } catch (err) {
      if (err.message.includes('429')) {
        setError(isAr ? 'محاولات كثيرة جداً. يرجى المحاولة لاحقاً.' : 'Too many login attempts. Please try again later.');
      } else {
        setError(isAr ? 'اسم المستخدم أو كلمة المرور غير صحيحة.' : 'Invalid username or password.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card-wrapper">
        <div className="login-card">
          <div className="login-card-glow" />
          <div className="login-header">
            <button className="login-back-btn" onClick={onBack} title={isAr ? 'العودة' : 'Back'}>
              {isAr ? '←' : '←'}
            </button>
            <div className="login-icon">🔑</div>
            <h2 className="login-title">
              {isAr ? 'تسجيل دخول المشرف' : 'Admin Portal'}
            </h2>
            <p className="login-subtitle">
              {isAr ? 'أدخل بيانات الاعتماد للوصول إلى لوحة التحكم' : 'Secure authorization required'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && (
              <div className="login-error-alert">
                <span className="error-alert-icon">⚠️</span>
                <span className="error-alert-text">{error}</span>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="username">
                {isAr ? 'اسم المستخدم' : 'Username'}
              </label>
              <input
                type="text"
                id="username"
                className="login-input"
                placeholder={isAr ? 'أدخل اسم المستخدم' : 'Enter username'}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">
                {isAr ? 'كلمة المرور' : 'Password'}
              </label>
              <input
                type="password"
                id="password"
                className="login-input"
                placeholder={isAr ? 'أدخل كلمة المرور' : 'Enter password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              className={`login-submit-btn ${loading ? 'loading' : ''}`}
              disabled={loading}
            >
              {loading ? (
                <span className="spinner-sm" />
              ) : (
                <span>{isAr ? 'تسجيل الدخول' : 'Access Dashboard'}</span>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
