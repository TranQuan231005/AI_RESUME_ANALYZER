import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { ApiRequestError, authenticate } from '../api/auth';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const { token, user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (token && user) {
    return <Navigate to={user.role === 'ADMIN' ? '/admin' : '/dashboard'} replace />;
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const response = await authenticate(email, password);
      login(response.accessToken, response.user);
      navigate(response.user.role === 'ADMIN' ? '/admin' : '/dashboard', { replace: true });
    } catch (caught) {
      setError(caught instanceof ApiRequestError ? caught.message : 'Unable to sign in.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Sign in</h1>
          <p>Sign in to your account to analyze resumes and review history</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
          <div>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>
          {error && <p role="alert">{error}</p>}
          <button type="submit" disabled={isSubmitting} style={{ width: '100%', marginTop: '0.5rem' }}>
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <div className="demo-credentials">
          <div style={{ fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-primary)' }}>Demo Accounts:</div>
          <div>👤 User: <code>user@example.test</code> &bull; <code>User@123456</code></div>
          <div style={{ marginTop: '0.25rem' }}>🛡️ Admin: <code>admin@example.test</code> &bull; <code>Admin@123456</code></div>
        </div>
      </div>
    </main>
  );
};
