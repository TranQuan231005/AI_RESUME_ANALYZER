import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { AdminPage } from './AdminPage';
import * as adminApi from '../api/admin';
import * as authContext from '../context/AuthContext';

jest.mock('../api/admin');
jest.mock('../context/AuthContext');

describe('AdminPage', () => {
  beforeEach(() => {
    (authContext.useAuth as jest.Mock).mockReturnValue({
      token: 'valid-admin-token',
      user: { id: 1, email: 'admin@test.com', fullName: 'Admin User', role: 'ADMIN' },
    });

    (adminApi.getAdminMetrics as jest.Mock).mockResolvedValue({
      totalAnalyses: 42,
      resumeAnalysesCount: 25,
      matchAnalysesCount: 17,
      fallbackRate: 0.048,
      avgLatencyMs: 250.5,
      p95LatencyMs: 500.0,
    });

    (adminApi.getAdminUsers as jest.Mock).mockResolvedValue({
      items: [{ id: 1, email: 'admin@test.com', fullName: 'Admin User', role: 'ADMIN' }],
      page: 0,
      size: 10,
      totalItems: 1,
      totalPages: 1,
    });

    (adminApi.getAdminAnalyses as jest.Mock).mockResolvedValue({
      items: [{
        id: 1,
        analysisType: 'RESUME',
        fileName: 'resume.pdf',
        candidateName: 'Alex',
        predictedField: 'Web Development',
        resumeScore: 88,
        matchScore: null,
        targetRole: null,
        aiProvider: 'OLLAMA',
        usedFallback: false,
        createdAt: '2026-08-31T12:00:00Z',
      }],
      page: 0,
      size: 10,
      totalItems: 1,
      totalPages: 1,
    });
  });

  test('renders metrics cards, users, and analyses after loading', async () => {
    render(<AdminPage />);

    expect(screen.getByText('Admin dashboard')).toBeTruthy();

    await waitFor(() => {
      expect(screen.getByText('42')).toBeTruthy();
      expect(screen.getByText('4.8%')).toBeTruthy();
      expect(screen.getByText('admin@test.com')).toBeTruthy();
      expect(screen.getByText('resume.pdf')).toBeTruthy();
      expect(screen.getByRole('region', { name: 'Registered users table' })).toBeTruthy();
      expect(screen.getByRole('region', { name: 'Recent analyses table' })).toBeTruthy();
    });
  });

  test('offers a retry after a failed load and shows empty tables after recovery', async () => {
    jest.mocked(adminApi.getAdminMetrics).mockRejectedValueOnce(new Error('Service unavailable'));
    jest.mocked(adminApi.getAdminUsers).mockResolvedValue({ items: [], page: 0, size: 10, totalItems: 0, totalPages: 0 });
    jest.mocked(adminApi.getAdminAnalyses).mockResolvedValue({ items: [], page: 0, size: 10, totalItems: 0, totalPages: 0 });
    render(<AdminPage />);
    expect(await screen.findByRole('alert')).toHaveTextContent('Service unavailable');
    fireEvent.click(screen.getByRole('button', { name: /try again/i }));
    expect(await screen.findByText('No registered users.')).toBeInTheDocument();
    expect(screen.getByText('No analyses yet.')).toBeInTheDocument();
  });
});
