import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import normalFixtureJson from '../../../contracts/fixtures/resume-analysis-result.json';
import fallbackFixtureJson from '../../../contracts/fixtures/resume-analysis-result-fallback.json';
import type { ResumeAnalysisResult } from '../types/analysis';
import { ResumeResultPage } from './ResumeResultPage';

const normalFixture = normalFixtureJson as ResumeAnalysisResult;
const fallbackFixture = fallbackFixtureJson as ResumeAnalysisResult;

const renderWithState = (state?: unknown) => render(
  <MemoryRouter initialEntries={[{ pathname: '/resume/result', state }]}>
    <ResumeResultPage />
  </MemoryRouter>,
);

describe('ResumeResultPage', () => {
  test.each([
    ['normal', normalFixture, false],
    ['fallback', fallbackFixture, true],
  ])('renders the frozen %s fixture passed through router state', (_name, result, fallback) => {
    renderWithState({ result });

    expect(screen.getByText('alex_resume.pdf')).toBeTruthy();
    expect(screen.getByText('Overall Score: 71/100')).toBeTruthy();
    expect(Boolean(screen.queryByTestId('fallback-badge'))).toBe(fallback);
  });

  test('shows an empty state with a dashboard link on direct access', () => {
    renderWithState();

    expect(screen.getByText('No analysis result is available.')).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Return to dashboard' }).getAttribute('href'))
      .toBe('/dashboard');
  });

  test('treats incomplete router data as an empty state', () => {
    renderWithState({ result: { fileName: 'incomplete.pdf', resumeScore: 80 } });

    expect(screen.getByText('No analysis result is available.')).toBeTruthy();
  });

  test('renders loading and safe error route states', () => {
    const { unmount } = renderWithState({ loading: true });
    expect(screen.getByTestId('loading-state')).toBeTruthy();
    unmount();

    renderWithState({ error: 'Analysis service is unavailable.' });
    expect(screen.getByRole('alert').textContent).toContain('Analysis service is unavailable.');
  });
});
