import React from 'react';
import { render, screen } from '@testing-library/react';
import normalFixtureJson from '../../../contracts/fixtures/match-result.json';
import fallbackFixtureJson from '../../../contracts/fixtures/match-result-fallback.json';
import type { MatchResult as MatchResultType } from '../types/analysis';
import { MatchResult } from './MatchResult';

const normalFixture = normalFixtureJson as MatchResultType;
const fallbackFixture = fallbackFixtureJson as MatchResultType;

describe('MatchResult', () => {
  test('renders loading, error, and empty states', () => {
    const { rerender, container } = render(
      <MatchResult loading error={null} result={null} />,
    );
    expect(screen.getByTestId('loading-state')).toBeTruthy();

    rerender(<MatchResult loading={false} error="Failed to process" result={null} />);
    expect(screen.getByRole('alert').textContent).toContain('Failed to process');

    rerender(<MatchResult loading={false} error={null} result={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders every match section from the normal fixture', () => {
    render(<MatchResult loading={false} error={null} result={normalFixture} />);

    expect(screen.getByText('Match Score: 67/100')).toBeTruthy();
    expect(screen.getByText('Target Role: Data Analyst')).toBeTruthy();
    expect(screen.getByTestId('matched-skills').textContent).toContain('Python');
    expect(screen.getByTestId('missing-skills').textContent).toContain('Power BI');
    expect(screen.getByTestId('ats-keywords').textContent).toContain('data visualization');
    expect(screen.getByTestId('strengths').textContent).toContain('Strong core programming');
    expect(screen.getByTestId('weaknesses').textContent).toContain('Missing business intelligence');
    expect(screen.getByTestId('match-recommendations').textContent).toContain('Add a dedicated project');
    expect(screen.queryByTestId('fallback-badge')).toBeNull();
  });

  test('shows the fallback badge from ai.usedFallback', () => {
    render(<MatchResult loading={false} error={null} result={fallbackFixture} />);

    expect(screen.getByTestId('fallback-badge').textContent).toBe('Fallback Mode');
  });

  test('renders jdFileName when provided', () => {
    const resultWithJd: MatchResultType = {
      ...normalFixture,
      fileName: 'alex_cv.pdf',
      jdFileName: 'software_engineer_jd.pdf',
    };
    render(<MatchResult loading={false} error={null} result={resultWithJd} />);

    expect(screen.getByTestId('jd-filename').textContent).toContain('software_engineer_jd.pdf');
    expect(screen.getByRole('heading', { level: 2 }).textContent).toContain('alex_cv.pdf ↔ software_engineer_jd.pdf');
  });
});
