import React from 'react';
import { CheckCircle, Key, Lightbulb, TrendDown, TrendUp, WarningCircle } from '@phosphor-icons/react';
import type { MatchResult as MatchResultType } from '../types/analysis';
import { Alert, Badge, LoadingSkeleton, ScoreSummary } from './ui';
import styles from './Result.module.css';

interface MatchResultProps {
  loading: boolean;
  error: string | null;
  result: MatchResultType | null;
}

export const MatchResult: React.FC<MatchResultProps> = ({
  loading,
  error,
  result,
}) => {
  if (loading) {
    return <LoadingSkeleton label="Matching Resume with Job Description..." testId="loading-state" />;
  }

  if (error) {
    return <Alert tone="error" testId="error-state">Error: {error}</Alert>;
  }

  if (!result) {
    return null;
  }

  const {
    fileName,
    targetRole,
    matchScore,
    matchedSkills,
    missingSkills,
    atsKeywords,
    strengths,
    weaknesses,
    recommendations,
    ai,
  } = result;

  return (
    <article className={styles.result} data-testid="match-result">
      {ai?.usedFallback && (
        <Alert tone="warning">
          <div className={styles.fallback}><strong data-testid="fallback-badge">Fallback Mode</strong><p>The local rule-based engine produced this result because the AI provider was unavailable.</p></div>
        </Alert>
      )}

      <header className={styles.documentHeader}>
        <div>
          <h2>{fileName} {result.jdFileName ? `↔ ${result.jdFileName}` : ''}</h2>
          <p>Target Role: {targetRole}</p>
        </div>
        <div className={styles.meta}><Badge tone="accent">Job match</Badge>
        {result.jdFileName && (
          <p data-testid="jd-filename">
            Job Description Document: <strong>{result.jdFileName}</strong>
          </p>
        )}</div>
      </header>

      <ScoreSummary score={matchScore} label="Match Score" hint="A comparison of resume evidence, required skills, and ATS language." />

      <div className={styles.contentGrid}>
      <section className={styles.contentSection} data-testid="matched-skills">
        <h3><CheckCircle size={19} weight="bold" aria-hidden="true" />Matched Skills ({matchedSkills.length})</h3>
        {matchedSkills.length === 0 ? (
          <p>No matching skills found.</p>
        ) : (
          <ul className={styles.tags}>
            {matchedSkills.map((skill, index) => (
              <li className={`${styles.tag} ${styles.tagSuccess}`} key={`matched-${skill}-${index}`}>{skill}</li>
            ))}
          </ul>
        )}
      </section>

      <section className={styles.contentSection} data-testid="missing-skills">
        <h3><WarningCircle size={19} weight="bold" aria-hidden="true" />Missing Skills ({missingSkills.length})</h3>
        {missingSkills.length === 0 ? (
          <p>No missing skills identified.</p>
        ) : (
          <ul className={styles.tags}>
            {missingSkills.map((skill, index) => (
              <li className={`${styles.tag} ${styles.tagDanger}`} key={`missing-${skill}-${index}`}>{skill}</li>
            ))}
          </ul>
        )}
      </section>

      {atsKeywords && atsKeywords.length > 0 && (
        <section className={`${styles.contentSection} ${styles.contentSectionWide}`} data-testid="ats-keywords">
          <h3><Key size={19} weight="bold" aria-hidden="true" />ATS Keywords</h3>
          <ul className={styles.tags}>
            {atsKeywords.map((kw, index) => (
              <li className={styles.tag} key={`ats-${kw}-${index}`}>{kw}</li>
            ))}
          </ul>
        </section>
      )}

      {strengths && strengths.length > 0 && (
        <section className={styles.contentSection} data-testid="strengths">
          <h3><TrendUp size={19} weight="bold" aria-hidden="true" />Key Strengths</h3>
          <ul className={styles.recommendations}>
            {strengths.map((str, index) => (
              <li key={`strength-${index}`}>{str}</li>
            ))}
          </ul>
        </section>
      )}

      {weaknesses && weaknesses.length > 0 && (
        <section className={styles.contentSection} data-testid="weaknesses">
          <h3><TrendDown size={19} weight="bold" aria-hidden="true" />Identified Gaps</h3>
          <ul className={styles.recommendations}>
            {weaknesses.map((weak, index) => (
              <li key={`weakness-${index}`}>{weak}</li>
            ))}
          </ul>
        </section>
      )}

      {recommendations && recommendations.length > 0 && (
        <section className={`${styles.contentSection} ${styles.contentSectionWide}`} data-testid="match-recommendations">
          <h3><Lightbulb size={19} weight="bold" aria-hidden="true" />Actionable Recommendations</h3>
          <ul className={styles.recommendations}>
            {recommendations.map((rec, index) => (
              <li key={`rec-${index}`}>{rec}</li>
            ))}
          </ul>
        </section>
      )}
      </div>
    </article>
  );
};
