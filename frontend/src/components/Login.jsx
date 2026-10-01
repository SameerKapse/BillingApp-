import React, { useState } from 'react';
import { api } from '../api';
import { LogIn, UserPlus, AlertCircle, ShieldCheck } from 'lucide-react';

export default function Login({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await api.register(username, password);
        // Automatically login after register
        const res = await api.login(username, password);
        onLoginSuccess(res.user);
      } else {
        const res = await api.login(username, password);
        onLoginSuccess(res.user);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
          <ShieldCheck size={48} color="#2563eb" style={{ margin: '0 auto' }} />
        </div>
        <h2 className="auth-title">
          {isRegister ? 'Create Account' : 'Billing Portal Login'}
        </h2>
        <p className="auth-subtitle">
          {isRegister
            ? 'Sign up to start generating invoices'
            : 'Enter your credentials to access your billing dashboard'}
        </p>

        {error && (
          <div className="alert alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: '1.25rem' }}>
            <label>Username</label>
            <input
              type="text"
              className="input-field"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label>Password</label>
            <input
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginBottom: '1.25rem' }}
            disabled={loading}
          >
            {loading ? (
              'Processing...'
            ) : isRegister ? (
              <>
                <UserPlus size={18} /> Register & Log In
              </>
            ) : (
              <>
                <LogIn size={18} /> Sign In
              </>
            )}
          </button>
        </form>

        <div style={{ textAlign: 'center', fontSize: '0.875rem' }}>
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError('');
            }}
            style={{
              background: 'none',
              border: 'none',
              color: '#2563eb',
              cursor: 'pointer',
              fontWeight: '500',
              textDecoration: 'underline',
            }}
          >
            {isRegister
              ? 'Already have an account? Sign in'
              : "Don't have an account? Register"}
          </button>
        </div>

        {!isRegister && (
          <div
            style={{
              marginTop: '1.5rem',
              padding: '0.75rem',
              background: '#f8fafc',
              borderRadius: '6px',
              border: '1px solid #e2e8f0',
              fontSize: '0.8rem',
              color: '#64748b',
              textAlign: 'center',
            }}
          >
            Default Demo Account: <b>admin</b> / <b>admin123</b>
          </div>
        )}
      </div>
    </div>
  );
}
