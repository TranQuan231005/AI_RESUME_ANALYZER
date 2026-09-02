import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { uploadResume, matchJobDescription, getHistory } from '../api/analysis';
import type { PagedAnalysisSummary } from '../types/analysis';

export const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'resume' | 'match' | 'history'>('resume');

  // Resume analysis state
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  // Match analysis state
  const [matchFile, setMatchFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>('');
  const [targetRole, setTargetRole] = useState<string>('');

  // History state
  const [history, setHistory] = useState<PagedAnalysisSummary | null>(null);
  const [historyLoading, setHistoryLoading] = useState<boolean>(false);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const { token, logout } = useAuth();

  useEffect(() => {
    if (activeTab === 'history' && token) {
      loadHistory();
    }
  }, [activeTab, token]);

  const loadHistory = async () => {
    if (!token) return;
    setHistoryLoading(true);
    try {
      const data = await getHistory(token, 0, 10);
      setHistory(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load history.');
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleResumeFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        setError('Please select a valid PDF file.');
        setResumeFile(null);
        return;
      }
      setResumeFile(selectedFile);
      setError(null);
    }
  };

  const handleMatchFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        setError('Please select a valid PDF file.');
        setMatchFile(null);
        return;
      }
      setMatchFile(selectedFile);
      setError(null);
    }
  };

  const handleResumeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!resumeFile) {
      setError('Please select a PDF file before submitting.');
      return;
    }

    if (!token) {
      setError('Authentication token is missing. Please log in again.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await uploadResume(resumeFile, token);
      navigate('/resume/result', { state: { result: (response as any).result || response } });
    } catch (err: any) {
      if (err?.status === 401) {
        if (logout) logout();
        navigate('/login');
        return;
      }
      setError(err?.message || 'Failed to upload resume. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!matchFile) {
      setError('Please select a PDF file before submitting.');
      return;
    }

    if (!jobDescription || jobDescription.trim().length < 50) {
      setError('Job description must be at least 50 characters.');
      return;
    }

    if (!token) {
      setError('Authentication token is missing. Please log in again.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await matchJobDescription(
        matchFile,
        jobDescription,
        targetRole.trim() || undefined,
        token
      );
      navigate('/match/result', { state: { result: (response as any).result || response } });
    } catch (err: any) {
      if (err?.status === 401) {
        if (logout) logout();
        navigate('/login');
        return;
      }
      setError(err?.message || 'Failed to match resume with job description.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section>
      <h1>Resume dashboard</h1>
      <p>Analyze a resume and review your previous results.</p>
      <Link to="/resume/result">View latest result</Link>

      <nav style={{ display: 'flex', gap: '1rem', margin: '1rem 0' }}>
        <button
          type="button"
          onClick={() => { setActiveTab('resume'); setError(null); }}
          style={{ fontWeight: activeTab === 'resume' ? 'bold' : 'normal' }}
        >
          Resume Scoring
        </button>
        <button
          type="button"
          onClick={() => { setActiveTab('match'); setError(null); }}
          style={{ fontWeight: activeTab === 'match' ? 'bold' : 'normal' }}
        >
          Job Match & ATS
        </button>
        <button
          type="button"
          onClick={() => { setActiveTab('history'); setError(null); }}
          style={{ fontWeight: activeTab === 'history' ? 'bold' : 'normal' }}
        >
          Analysis History
        </button>
      </nav>

      {error && <p role="alert" style={{ color: 'red' }}>{error}</p>}

      {activeTab === 'resume' && (
        <form onSubmit={handleResumeSubmit}>
          <div>
            <label htmlFor="resume-file">Upload Resume (PDF)</label>
            <input
              id="resume-file"
              type="file"
              accept="application/pdf"
              onChange={handleResumeFileChange}
              disabled={isLoading}
            />
          </div>

          <button type="submit" disabled={isLoading || !resumeFile}>
            {isLoading ? 'Uploading...' : 'Upload Resume'}
          </button>
        </form>
      )}

      {activeTab === 'match' && (
        <form onSubmit={handleMatchSubmit} data-testid="match-form">
          <div>
            <label htmlFor="match-resume-file">Upload Resume (PDF)</label>
            <input
              id="match-resume-file"
              type="file"
              accept="application/pdf"
              onChange={handleMatchFileChange}
              disabled={isLoading}
            />
          </div>

          <div style={{ marginTop: '1rem' }}>
            <label htmlFor="target-role">Target Role (Optional)</label>
            <input
              id="target-role"
              type="text"
              placeholder="e.g. Senior Frontend Developer"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              disabled={isLoading}
              style={{ display: 'block', width: '100%', maxWidth: '400px', margin: '0.25rem 0' }}
            />
          </div>

          <div style={{ marginTop: '1rem' }}>
            <label htmlFor="job-description">Job Description (min 50 chars)</label>
            <textarea
              id="job-description"
              rows={6}
              placeholder="Paste the full job description or requirements here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              disabled={isLoading}
              style={{ display: 'block', width: '100%', maxWidth: '600px', margin: '0.25rem 0' }}
            />
          </div>

          <button type="submit" disabled={isLoading || !matchFile || jobDescription.trim().length < 50}>
            {isLoading ? 'Matching...' : 'Analyze Match'}
          </button>
        </form>
      )}

      {activeTab === 'history' && (
        <section data-testid="history-tab">
          <h2>Your Analysis History</h2>
          {historyLoading && <p role="status">Loading history...</p>}
          {history && history.items.length === 0 && <p>No previous analyses found.</p>}
          {history && history.items.length > 0 && (
            <ul>
              {history.items.map((item) => (
                <li key={item.id} style={{ margin: '0.5rem 0' }}>
                  <strong>[{item.analysisType}]</strong> {item.fileName} &mdash;{' '}
                  {item.analysisType === 'RESUME' ? `Score: ${item.resumeScore}/100` : `Match: ${item.matchScore}/100`}
                  {' '}({new Date(item.createdAt).toLocaleDateString()})
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </section>
  );
};