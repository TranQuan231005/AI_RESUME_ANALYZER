import React from 'react';
import { ArrowLeft } from '@phosphor-icons/react';
import { Link, useLocation } from 'react-router-dom';
import { ResumeResult } from '../components/ResumeResult';
import { EmptyState, PageHeader } from '../components/ui';
import type { ResumeAnalysisResult } from '../types/analysis';
import styles from './ResultPage.module.css';

interface ResumeResultRouteState {
  result?: ResumeAnalysisResult;
  loading?: boolean;
  error?: string | null;
}

const isResumeResult = (value: unknown): value is ResumeAnalysisResult => {
  if (!value || typeof value !== 'object') return false;
  const result = value as Partial<ResumeAnalysisResult>;
  const scoreKeys = [
    'contact',
    'summary',
    'skills',
    'education',
    'experience',
    'projects',
    'achievementsCertifications',
    'quantifiedImpact',
    'total',
  ] as const;
  const scoreBreakdown = result.scoreBreakdown as unknown as Record<string, unknown> | null;
  const ai = result.ai as unknown as Record<string, unknown> | null;
  return (
    typeof result.fileName === 'string' &&
    typeof result.resumeScore === 'number' &&
    typeof result.predictedField === 'string' &&
    Array.isArray(result.skills) &&
    Array.isArray(result.fieldEvidence) &&
    Array.isArray(result.recommendedSkills) &&
    Array.isArray(result.recommendations) &&
    scoreBreakdown !== null &&
    typeof scoreBreakdown === 'object' &&
    scoreKeys.every((key) => typeof scoreBreakdown[key] === 'number') &&
    ai !== null &&
    typeof ai === 'object' &&
    typeof ai.usedFallback === 'boolean'
  );
};

export const ResumeResultPage: React.FC = () => {
  const location = useLocation();
  const state = (location.state ?? {}) as ResumeResultRouteState;
  const result = isResumeResult(state.result) ? state.result : null;
  const error = typeof state.error === 'string' ? state.error : null;

  if (!state.loading && !error && !result) {
    return (
      <section className={styles.page}>
        <PageHeader title="Resume analysis result" description="Review the quality signals found in your resume." />
        <EmptyState title="No analysis result is available." description="Upload a resume from your dashboard to generate a new result." action={<Link className={styles.backLink} to="/dashboard"><ArrowLeft size={17} weight="bold" aria-hidden="true" />Return to dashboard</Link>} />
      </section>
    );
  }

  return (
    <section className={styles.page}>
      <PageHeader title="Resume analysis result" description="Review the quality signals found in your resume." />
      <ResumeResult loading={state.loading === true} error={error} result={result} />
      <Link className={styles.backLink} to="/dashboard"><ArrowLeft size={17} weight="bold" aria-hidden="true" />Return to dashboard</Link>
    </section>
  );
};
