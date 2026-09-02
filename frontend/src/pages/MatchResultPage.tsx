import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MatchResult } from '../components/MatchResult';
import type { MatchResult as MatchResultType } from '../types/analysis';

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
      <section>
        <h1>Job Match Result</h1>
        <p>No match result is available.</p>
        <Link to="/dashboard">Return to dashboard</Link>
      </section>
    );
  }

  return (
    <section>
      <h1>Job Match Result</h1>
      <MatchResult loading={state.loading === true} error={error} result={result} />
      <Link to="/dashboard">Return to dashboard</Link>
    </section>
  );
};
