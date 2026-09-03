import React from 'react';
import { ArrowLeft } from '@phosphor-icons/react';
import { Link, useLocation } from 'react-router-dom';
import { MatchResult } from '../components/MatchResult';
import { EmptyState, PageHeader } from '../components/ui';
import type { MatchResult as MatchResultType } from '../types/analysis';
import styles from './ResultPage.module.css';

interface MatchResultRouteState {
  result?: MatchResultType;
  loading?: boolean;
  error?: string | null;
}

export const MatchResultPage: React.FC = () => {
  const location = useLocation();
  const state = (location.state ?? {}) as MatchResultRouteState;
  const result = state.result ?? null;
  const error = typeof state.error === 'string' ? state.error : null;

  if (!state.loading && !error && !result) {
    return (
      <section className={styles.page}>
        <PageHeader title="Job Match Result" description="See where the resume aligns with the target role and what is missing." />
        <EmptyState title="No match result is available." description="Run a job match from your dashboard to generate a new result." action={<Link className={styles.backLink} to="/dashboard"><ArrowLeft size={17} weight="bold" aria-hidden="true" />Return to dashboard</Link>} />
      </section>
    );
  }

  return (
    <section className={styles.page}>
      <PageHeader title="Job Match Result" description="See where the resume aligns with the target role and what is missing." />
      <MatchResult loading={state.loading === true} error={error} result={result} />
      <Link className={styles.backLink} to="/dashboard"><ArrowLeft size={17} weight="bold" aria-hidden="true" />Return to dashboard</Link>
    </section>
  );
};
