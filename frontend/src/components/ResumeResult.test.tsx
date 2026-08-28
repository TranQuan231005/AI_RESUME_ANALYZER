import React from 'react';
import { render, screen } from '@testing-library/react';
import normalFixtureJson from '../../../contracts/fixtures/resume-analysis-result.json';
import fallbackFixtureJson from '../../../contracts/fixtures/resume-analysis-result-fallback.json';
import type { ResumeAnalysisResult } from '../types/analysis';
import { ResumeResult } from './ResumeResult';

const normalFixture = normalFixtureJson as ResumeAnalysisResult;
const fallbackFixture = fallbackFixtureJson as ResumeAnalysisResult;

describe('ResumeResult', () => {
  test('renders loading, error, and empty states', () => {
    const { rerender, container } = render(
      <ResumeResult loading error={null} result={null} />,
    );
    expect(screen.getByTestId('loading-state')).toBeTruthy();

    rerender(<ResumeResult loading={false} error="Failed to process" result={null} />);
    expect(screen.getByRole('alert').textContent).toContain('Failed to process');

    rerender(<ResumeResult loading={false} error={null} result={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders every frozen result section from the normal fixture', () => {
    render(<ResumeResult loading={false} error={null} result={normalFixture} />);

    expect(screen.getByText('Overall Score: 71/100')).toBeTruthy();
    expect(screen.getByTestId('score-breakdown').textContent).toContain('Achievements: 5/10');
    expect(screen.getByTestId('score-breakdown').textContent).toContain('Impact: 8/15');
    expect(screen.getByTestId('evidence-section').textContent).toContain('Python, Pandas');
    expect(screen.getByTestId('recommended-skills').textContent).toContain('Machine Learning');
    expect(screen.getByTestId('recommendations').textContent).toContain('business impact');
    expect(screen.queryByTestId('fallback-badge')).toBeNull();
  });

  test('shows the fallback badge from ai.usedFallback', () => {
    render(<ResumeResult loading={false} error={null} result={fallbackFixture} />);

    expect(screen.getByTestId('fallback-badge').textContent).toBe('Fallback Mode');
    expect(screen.getByText('Git')).toBeTruthy();
  });
});
