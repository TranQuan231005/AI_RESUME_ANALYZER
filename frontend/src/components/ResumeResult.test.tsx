import React from 'react';
import { render } from '@testing-library/react';
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
    const { getByTestId } = render(
      <ResumeResult
        loading={true}
        error={null}
        scoreBreakdown={null}
        evidence={[]}
        recommendations={[]}
        recommendedSkills={[]}
      />
    );
    expect(getByTestId('loading-state')).toBeTruthy();
  });

  test('renders error state', () => {
    const { getByTestId } = render(
      <ResumeResult
        loading={false}
        error="Failed to process"
        scoreBreakdown={null}
        evidence={[]}
        recommendations={[]}
        recommendedSkills={[]}
      />
    );
    expect(getByTestId('error-state')).toBeTruthy();
  });

  test('renders score breakdown and fallback badge', () => {
    const { getByTestId, getByText } = render(
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
    expect(getByTestId('fallback-badge')).toBeTruthy();
    expect(getByText('Overall Score: 71/100')).toBeTruthy();
  });
});