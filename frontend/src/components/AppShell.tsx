import React from 'react';
import { FileMagnifyingGlass, SignOut } from '@phosphor-icons/react';
import { Link, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui';
import styles from './AppShell.module.css';

export const AppShell: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className={styles.shell}>
      <header className={styles.topbar}>
        <Link className={styles.brand} to={user?.role === 'ADMIN' ? '/admin' : '/dashboard'}>
          <span className={styles.mark}><FileMagnifyingGlass size={18} weight="bold" aria-hidden="true" /></span>
          <span className={styles.brandText}>AI Resume Analyzer</span>
        </Link>
        <nav className={styles.account} aria-label="Account navigation">
          <span className={styles.identity}>
            <strong>{user?.fullName}</strong>
            <span>{user?.role}</span>
          </span>
          <Button type="button" variant="secondary" icon={<SignOut size={18} weight="bold" aria-hidden="true" />} onClick={logout}>Log out</Button>
        </nav>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
};
