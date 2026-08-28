import React from 'react';
import type { ResumeAnalysisResult } from '../types/analysis';

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
    return <p role="status" data-testid="loading-state">Analyzing Resume...</p>;
  }

  if (error) {
    return <p role="alert" data-testid="error-state">Error: {error}</p>;
  }

  if (!result) {
    return null;
  }

  const { ai, fieldEvidence, recommendations, recommendedSkills, scoreBreakdown } = result;

  return (
    <article data-testid="resume-result">
      {ai.usedFallback && (
        <strong data-testid="fallback-badge">
          Fallback Mode
        </strong>
      )}

      <header>
        <h2>{result.fileName}</h2>
        <p>{result.candidateName ?? 'Candidate name unavailable'}</p>
        <p>Predicted field: {result.predictedField}</p>
      </header>

      <h3>Overall Score: {result.resumeScore}/100</h3>
      <progress aria-label="Overall resume score" value={result.resumeScore} max={100} />

      <section data-testid="score-breakdown" aria-labelledby="score-breakdown-heading">
        <h3 id="score-breakdown-heading">Score breakdown</h3>
        <div>Contact: {scoreBreakdown.contact}/5</div>
        <div>Summary: {scoreBreakdown.summary}/10</div>
        <div>Skills: {scoreBreakdown.skills}/15</div>
        <div>Education: {scoreBreakdown.education}/10</div>
        <div>Experience: {scoreBreakdown.experience}/20</div>
        <div>Projects: {scoreBreakdown.projects}/15</div>
        <div>Achievements: {scoreBreakdown.achievementsCertifications}/10</div>
        <div>Impact: {scoreBreakdown.quantifiedImpact}/15</div>
      </section>

      {fieldEvidence.length > 0 && (
        <section data-testid="evidence-section">
          <h3>Evidence</h3>
          <ul>
            {fieldEvidence.map((item, index) => (
              <li key={`${item.field}-${index}`}>
                {item.field}: {item.matchedSkills.join(', ')} ({Math.round(item.confidence * 100)}%)
              </li>
            ))}
          </ul>
        </section>
      )}

      {recommendedSkills.length > 0 && (
        <section data-testid="recommended-skills">
          <h3>Recommended Skills</h3>
          <ul>
            {recommendedSkills.map((skill, idx) => (
              <li key={idx}>{skill}</li>
            ))}
          </ul>
        </section>
      )}

      {recommendations.length > 0 && (
        <section data-testid="recommendations">
          <h3>Recommendations</h3>
          <ul>
            {recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
};
