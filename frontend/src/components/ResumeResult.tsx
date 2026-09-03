import React from 'react';
import { Lightbulb, MagnifyingGlass, Sparkle } from '@phosphor-icons/react';
import type { ResumeAnalysisResult } from '../types/analysis';
import { Alert, Badge, LoadingSkeleton, ScoreSummary } from './ui';
import styles from './Result.module.css';

interface ResumeResultProps {
  loading: boolean;
  error: string | null;
  result: ResumeAnalysisResult | null;
}

export const ResumeResult: React.FC<ResumeResultProps> = ({
  loading,
  error,
  result,
}) => {
  if (loading) {
    return <LoadingSkeleton label="Analyzing Resume..." testId="loading-state" />;
  }

  if (error) {
    return <Alert tone="error" testId="error-state">Error: {error}</Alert>;
  }

  if (!result) {
    return null;
  }

  const { ai, fieldEvidence, recommendations, recommendedSkills, scoreBreakdown } = result;

  return (
    <article className={styles.result} data-testid="resume-result">
      {ai.usedFallback && (
        <Alert tone="warning">
          <div className={styles.fallback}><strong data-testid="fallback-badge">Fallback Mode</strong><p>The local rule-based engine produced this result because the AI provider was unavailable.</p></div>
        </Alert>
      )}

      <header className={styles.documentHeader}>
        <div><h2>{result.fileName}</h2><p>{result.candidateName ?? 'Candidate name unavailable'}</p></div>
        <div className={styles.meta}><Badge tone="accent">{result.predictedField}</Badge><p>Predicted field</p></div>
      </header>

      <ScoreSummary score={result.resumeScore} label="Overall Score" hint="A structured score across eight resume quality signals." />

      <section className={styles.breakdown} data-testid="score-breakdown" aria-labelledby="score-breakdown-heading">
        <h3 className={styles.sectionTitle} id="score-breakdown-heading">Score breakdown</h3>
        <div className={styles.metric}><span>Contact: </span><strong>{scoreBreakdown.contact}/5</strong></div>
        <div className={styles.metric}><span>Summary: </span><strong>{scoreBreakdown.summary}/10</strong></div>
        <div className={styles.metric}><span>Skills: </span><strong>{scoreBreakdown.skills}/15</strong></div>
        <div className={styles.metric}><span>Education: </span><strong>{scoreBreakdown.education}/10</strong></div>
        <div className={styles.metric}><span>Experience: </span><strong>{scoreBreakdown.experience}/20</strong></div>
        <div className={styles.metric}><span>Projects: </span><strong>{scoreBreakdown.projects}/15</strong></div>
        <div className={styles.metric}><span>Achievements: </span><strong>{scoreBreakdown.achievementsCertifications}/10</strong></div>
        <div className={styles.metric}><span>Impact: </span><strong>{scoreBreakdown.quantifiedImpact}/15</strong></div>
      </section>

      <div className={styles.contentGrid}>
        {fieldEvidence.length > 0 && (
        <section className={styles.contentSection} data-testid="evidence-section">
          <h3><MagnifyingGlass size={19} weight="bold" aria-hidden="true" />Evidence</h3>
          <ul className={styles.tags}>
            {fieldEvidence.map((item, index) => (
              <li className={styles.tag} key={`${item.field}-${index}`}>
                {item.field}: {item.matchedSkills.join(', ')} ({Math.round(item.confidence * 100)}%)
              </li>
            ))}
          </ul>
        </section>
        )}

      {recommendedSkills.length > 0 && (
        <section className={styles.contentSection} data-testid="recommended-skills">
          <h3><Sparkle size={19} weight="bold" aria-hidden="true" />Recommended Skills</h3>
          <ul className={styles.tags}>
            {recommendedSkills.map((skill, idx) => (
              <li className={`${styles.tag} ${styles.tagSuccess}`} key={idx}>{skill}</li>
            ))}
          </ul>
        </section>
      )}

      {recommendations.length > 0 && (
        <section className={`${styles.contentSection} ${styles.contentSectionWide}`} data-testid="recommendations">
          <h3><Lightbulb size={19} weight="bold" aria-hidden="true" />Recommendations</h3>
          <ul className={styles.recommendations}>
            {recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </section>
      )}
      </div>
    </article>
  );
};
