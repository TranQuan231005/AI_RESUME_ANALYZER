import React, { useState } from 'react';
import { FileMagnifyingGlass, SignIn } from '@phosphor-icons/react';
import { Navigate, useNavigate } from 'react-router-dom';
import { ApiRequestError, authenticate } from '../api/auth';
import { Alert, Button } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import styles from './LoginPage.module.css';

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
    <main className={styles.page}>
      <section className={styles.story} aria-label="Product introduction">
        <div className={styles.brand}>
          <span className={styles.brandMark}><FileMagnifyingGlass size={20} weight="bold" aria-hidden="true" /></span>
          AI Resume Analyzer
        </div>
        <div className={styles.statement}>
          <h1>Turn experience into a stronger application.</h1>
          <p>Analyze resume quality, identify missing skills, and compare your experience with a real job description.</p>
        </div>
        <p className={styles.note}>Local AI. Structured feedback. No resume storage.</p>
      </section>
      <section className={styles.formPane}>
        <div className={styles.card}>
          <div className={styles.heading}>
            <h2>Sign in</h2>
            <p>Continue to your analysis workspace.</p>
          </div>
          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.field}>
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
            <div className={styles.field}>
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
            {error && <Alert tone="error">{error}</Alert>}
            <Button type="submit" disabled={isSubmitting} fullWidth icon={<SignIn size={19} weight="bold" aria-hidden="true" />}>
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>
          <div className={styles.demo}>
            <p className={styles.demoTitle}>Demo accounts</p>
            <div className={styles.account}><strong>User</strong><code>user@example.test / User@123456</code></div>
            <div className={styles.account}><strong>Admin</strong><code>admin@example.test / Admin@123456</code></div>
          </div>
        </div>
      </section>
    </main>
  );
};
