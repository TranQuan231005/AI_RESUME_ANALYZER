import React from 'react';

interface ScoreBreakdown {
  contact: number;
  summary: number;
  skills: number;
  education: number;
  experience: number;
  projects: number;
  achievementsCertifications: number;
  quantifiedImpact: number;
  total: number;
}

interface ResumeResultProps {
  loading: boolean;
  error: string | null;
  isFallback?: boolean;
  scoreBreakdown: ScoreBreakdown | null;
  evidence: string[];
  recommendations: string[];
  recommendedSkills: string[];
}

export const ResumeResult: React.FC<ResumeResultProps> = ({
  loading,
  error,
  isFallback = false,
  scoreBreakdown,
  evidence,
  recommendations,
  recommendedSkills,
}) => {
  if (loading) {
    return <div data-testid="loading-state">Analyzing Resume...</div>;
  }

  if (error) {
    return <div data-testid="error-state">Error: {error}</div>;
  }

  if (!scoreBreakdown) {
    return null;
  }

  return (
    <div data-testid="resume-result">
      {isFallback && (
        <span data-testid="fallback-badge" className="badge-warning">
          Fallback Mode
        </span>
      )}

      <h2>Overall Score: {scoreBreakdown.total}/100</h2>

      <div data-testid="score-breakdown">
        <div>Contact: {scoreBreakdown.contact}/5</div>
        <div>Summary: {scoreBreakdown.summary}/10</div>
        <div>Skills: {scoreBreakdown.skills}/15</div>
        <div>Education: {scoreBreakdown.education}/10</div>
        <div>Experience: {scoreBreakdown.experience}/20</div>
        <div>Projects: {scoreBreakdown.projects}/15</div>
        <div>Achievements: {scoreBreakdown.achievementsCertifications}/10</div>
        <div>Impact: {scoreBreakdown.quantifiedImpact}/15</div>
      </div>

      {evidence.length > 0 && (
        <div data-testid="evidence-section">
          <h3>Evidence</h3>
          <ul>
            {evidence.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {recommendedSkills.length > 0 && (
        <div data-testid="recommended-skills">
          <h3>Recommended Skills</h3>
          <ul>
            {recommendedSkills.map((skill, idx) => (
              <li key={idx}>{skill}</li>
            ))}
          </ul>
        </div>
      )}

      {recommendations.length > 0 && (
        <div data-testid="recommendations">
          <h3>Recommendations</h3>
          <ul>
            {recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};