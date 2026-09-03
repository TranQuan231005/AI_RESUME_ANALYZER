import React from 'react';
import { ArrowLeft } from '@phosphor-icons/react';
import { Link } from 'react-router-dom';
import { EmptyState } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import styles from './ResultPage.module.css';

export const ForbiddenPage: React.FC = () => {
  const { user } = useAuth();
  const destination = user?.role === 'ADMIN' ? '/admin' : user ? '/dashboard' : '/login';
  return (
    <main className={`${styles.page} ${styles.standalone}`}>
      <EmptyState title="Access denied" description="Your account does not have permission to view this page." action={<Link className={styles.backLink} to={destination}><ArrowLeft size={17} weight="bold" aria-hidden="true" />Return home</Link>} />
    </main>
  );
};
