import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { DashboardPage } from './DashboardPage';
import * as AuthContextModule from '../context/AuthContext';
import * as analysisApi from '../api/analysis';
import type { PersistedResumeAnalysisResponse } from '../types/analysis';

jest.mock('../api/analysis');
jest.mock('../context/AuthContext');

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('DashboardPage', () => {
  const mockToken = 'fake-jwt-token';
  const mockLogout = jest.fn();

  const renderDashboard = (token: string | null = mockToken) => {
    jest.mocked(AuthContextModule.useAuth).mockReturnValue({
      token,
      user: null,
      login: jest.fn(),
      logout: mockLogout,
    });

    return render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/login" element={<div>Login Page</div>} />
          <Route path="/resume/result" element={<div>Result Page</div>} />
        </Routes>
      </MemoryRouter>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders dashboard title and file input', () => {
    renderDashboard();
    expect(screen.getByRole('heading', { name: /resume dashboard/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/upload resume \(pdf\)/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload resume/i })).toBeDisabled();
  });

  test('shows error when non-pdf file is selected', () => {
    renderDashboard();
    const input = screen.getByLabelText(/upload resume \(pdf\)/i);
    const txtFile = new File(['dummy content'], 'test.txt', { type: 'text/plain' });

    fireEvent.change(input, { target: { files: [txtFile] } });

    expect(screen.getByRole('alert')).toHaveTextContent('Please select a valid PDF file.');
    expect(screen.getByRole('button', { name: /upload resume/i })).toBeDisabled();
  });

  test('enables submit button when valid PDF is selected', () => {
    renderDashboard();
    const input = screen.getByLabelText(/upload resume \(pdf\)/i);
    const pdfFile = new File(['dummy pdf'], 'resume.pdf', { type: 'application/pdf' });

    fireEvent.change(input, { target: { files: [pdfFile] } });

    expect(screen.getByRole('button', { name: /upload resume/i })).toBeEnabled();
  });

  test('handles successful resume upload and navigates to result page', async () => {
    const mockResult = {
      fileName: 'resume.pdf',
      candidateName: null,
      candidateEmail: null,
      resumeScore: 85,
      predictedField: 'Web Development' as const,
      skills: ['React', 'TypeScript'],
      fieldEvidence: [],
      scoreBreakdown: {
        contact: 10,
        summary: 10,
        skills: 10,
        education: 10,
        experience: 10,
        projects: 10,
        achievementsCertifications: 10,
        quantifiedImpact: 15,
        total: 85,
      },
      recommendedSkills: [],
      recommendations: [],
      ai: {
        provider: 'RULE_BASED' as const,
        model: 'default',
        usedFallback: false,
        processingMs: 100,
      },
    };

    const mockResponse: PersistedResumeAnalysisResponse = {
      id: 1,
      createdAt: '2026-09-02T10:00:00.000Z',
      result: mockResult,
    };

    jest.mocked(analysisApi.uploadResume).mockResolvedValueOnce(mockResponse);

    renderDashboard();

    const input = screen.getByLabelText(/upload resume \(pdf\)/i);
    const pdfFile = new File(['dummy pdf'], 'resume.pdf', { type: 'application/pdf' });

    fireEvent.change(input, { target: { files: [pdfFile] } });

    const submitBtn = screen.getByRole('button', { name: /upload resume/i });
    fireEvent.click(submitBtn);

    expect(submitBtn).toBeDisabled();
    expect(screen.getByText(/uploading.../i)).toBeInTheDocument();

    await waitFor(() => {
      expect(analysisApi.uploadResume).toHaveBeenCalledWith(pdfFile, mockToken);
      expect(mockNavigate).toHaveBeenCalledWith('/resume/result', {
        state: { result: mockResult },
      });
    });
  });

  test('redirects to login on 401 unauthenticated error', async () => {
    const error401 = new Error('Unauthorized') as Error & { status?: number };
    error401.status = 401;

    jest.mocked(analysisApi.uploadResume).mockRejectedValueOnce(error401);

    renderDashboard();

    const input = screen.getByLabelText(/upload resume \(pdf\)/i);
    const pdfFile = new File(['dummy pdf'], 'resume.pdf', { type: 'application/pdf' });

    fireEvent.change(input, { target: { files: [pdfFile] } });
    fireEvent.click(screen.getByRole('button', { name: /upload resume/i }));

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  test('displays error message on upload failure', async () => {
    jest.mocked(analysisApi.uploadResume).mockRejectedValueOnce(
      new Error('Server error occurred')
    );

    renderDashboard();

    const input = screen.getByLabelText(/upload resume \(pdf\)/i);
    const pdfFile = new File(['dummy pdf'], 'resume.pdf', { type: 'application/pdf' });

    fireEvent.change(input, { target: { files: [pdfFile] } });
    fireEvent.click(screen.getByRole('button', { name: /upload resume/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Server error occurred');
    });
  });
});