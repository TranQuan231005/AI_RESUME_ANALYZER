import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, test, expect } from '@jest/globals';
import { ResumeResult } from './ResumeResult';

describe('ResumeResult Component', () => {
  const sampleScore = {
    contact: 5,
    summary: 8,
    skills: 12,
    education: 8,
    experience: 15,
    projects: 10,
    achievementsCertifications: 5,
    quantifiedImpact: 8,
    total: 71,
  };

  test('renders loading state', () => {
    render(
      <ResumeResult
        loading={true}
        error={null}
        scoreBreakdown={null}
        evidence={[]}
        recommendations={[]}
        recommendedSkills={[]}
      />
    );
    expect(screen.getByTestId('loading-state')).toBeTruthy();
  });

  test('renders error state', () => {
    render(
      <ResumeResult
        loading={false}
        error="Failed to process"
        scoreBreakdown={null}
        evidence={[]}
        recommendations={[]}
        recommendedSkills={[]}
      />
    );
    expect(screen.getByTestId('error-state')).toBeTruthy();
  });

  test('returns null when scoreBreakdown is null', () => {
    const { container } = render(
      <ResumeResult
        loading={false}
        error={null}
        scoreBreakdown={null}
        evidence={[]}
        recommendations={[]}
        recommendedSkills={[]}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  test('renders score breakdown and fallback badge', () => {
    render(
      <ResumeResult
        loading={false}
        error={null}
        isFallback={true}
        scoreBreakdown={sampleScore}
        evidence={['Found 3 years exp']}
        recommendations={['Add skills']}
        recommendedSkills={['Docker']}
      />
    );
    expect(screen.getByTestId('fallback-badge')).toBeTruthy();
    expect(screen.getByText('Overall Score: 71/100')).toBeTruthy();
    expect(screen.getByTestId('score-breakdown')).toBeTruthy();
    expect(screen.getByTestId('evidence-section')).toBeTruthy();
    expect(screen.getByTestId('recommended-skills')).toBeTruthy();
    expect(screen.getByTestId('recommendations')).toBeTruthy();
  });

  test('does not render fallback badge when isFallback is false', () => {
    render(
      <ResumeResult
        loading={false}
        error={null}
        isFallback={false}
        scoreBreakdown={sampleScore}
        evidence={[]}
        recommendations={[]}
        recommendedSkills={[]}
      />
    );
    expect(screen.queryByTestId('fallback-badge')).toBeNull();
  });

  test('does not render empty section containers', () => {
    render(
      <ResumeResult
        loading={false}
        error={null}
        scoreBreakdown={sampleScore}
        evidence={[]}
        recommendations={[]}
        recommendedSkills={[]}
      />
    );
    expect(screen.queryByTestId('evidence-section')).toBeNull();
    expect(screen.queryByTestId('recommended-skills')).toBeNull();
    expect(screen.queryByTestId('recommendations')).toBeNull();
  });
});