import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
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
    });
  });
});
