import React from 'react';
import type { MatchResult as MatchResultType } from '../types/analysis';

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
    return <p role="status" data-testid="loading-state">Matching Resume with Job Description...</p>;
  }

  if (error) {
    return <p role="alert" data-testid="error-state">Error: {error}</p>;
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
    <article data-testid="match-result">
      {ai?.usedFallback && (
        <strong data-testid="fallback-badge">
          Fallback Mode
        </strong>
      )}

      <header>
        <h2>{fileName} {result.jdFileName ? `↔ ${result.jdFileName}` : ''}</h2>
        <p>Target Role: {targetRole}</p>
        {result.jdFileName && (
          <p data-testid="jd-filename">
            Job Description Document: <strong>{result.jdFileName}</strong>
          </p>
        )}
      </header>

      <h3>Match Score: {matchScore}/100</h3>
      <progress aria-label="Job description match score" value={matchScore} max={100} />

      <section data-testid="matched-skills">
        <h3>Matched Skills ({matchedSkills.length})</h3>
        {matchedSkills.length === 0 ? (
          <p>No matching skills found.</p>
        ) : (
          <ul>
            {matchedSkills.map((skill, index) => (
              <li key={`matched-${skill}-${index}`}>{skill}</li>
            ))}
          </ul>
        )}
      </section>

      <section data-testid="missing-skills">
        <h3>Missing Skills ({missingSkills.length})</h3>
        {missingSkills.length === 0 ? (
          <p>No missing skills identified.</p>
        ) : (
          <ul>
            {missingSkills.map((skill, index) => (
              <li key={`missing-${skill}-${index}`}>{skill}</li>
            ))}
          </ul>
        )}
      </section>

      {atsKeywords && atsKeywords.length > 0 && (
        <section data-testid="ats-keywords">
          <h3>ATS Keywords</h3>
          <ul>
            {atsKeywords.map((kw, index) => (
              <li key={`ats-${kw}-${index}`}>{kw}</li>
            ))}
          </ul>
        </section>
      )}

      {strengths && strengths.length > 0 && (
        <section data-testid="strengths">
          <h3>Key Strengths</h3>
          <ul>
            {strengths.map((str, index) => (
              <li key={`strength-${index}`}>{str}</li>
            ))}
          </ul>
        </section>
      )}

      {weaknesses && weaknesses.length > 0 && (
        <section data-testid="weaknesses">
          <h3>Identified Gaps</h3>
          <ul>
            {weaknesses.map((weak, index) => (
              <li key={`weakness-${index}`}>{weak}</li>
            ))}
          </ul>
        </section>
      )}

      {recommendations && recommendations.length > 0 && (
        <section data-testid="match-recommendations">
          <h3>Actionable Recommendations</h3>
          <ul>
            {recommendations.map((rec, index) => (
              <li key={`rec-${index}`}>{rec}</li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
};
