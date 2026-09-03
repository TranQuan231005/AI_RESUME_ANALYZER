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
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdInputMode, setJdInputMode] = useState<'pdf' | 'text'>('pdf');
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
        setError('Please select a valid PDF file for Candidate Resume.');
        setMatchFile(null);
        return;
      }
      setMatchFile(selectedFile);
      setError(null);
    }
  };

  const handleJdFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        setError('Please select a valid PDF file for Job Description.');
        setJdFile(null);
        return;
      }
      setJdFile(selectedFile);
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

  const isJdValid = jdInputMode === 'pdf' ? !!jdFile : jobDescription.trim().length >= 50;

  const handleMatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!matchFile) {
      setError('Please select a Candidate Resume PDF file before submitting.');
      return;
    }

    if (jdInputMode === 'pdf' && !jdFile) {
      setError('Please select a Job Description PDF file.');
      return;
    }

    if (jdInputMode === 'text' && (!jobDescription || jobDescription.trim().length < 50)) {
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
        jdInputMode === 'text' ? jobDescription : undefined,
        targetRole.trim() || undefined,
        token,
        jdInputMode === 'pdf' ? jdFile : null
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

      <nav style={{ display: 'flex', gap: '0.75rem', margin: '1.25rem 0' }}>
        <button
          type="button"
          className={activeTab === 'resume' ? 'input-mode-btn active' : 'input-mode-btn'}
          onClick={() => { setActiveTab('resume'); setError(null); }}
        >
          📊 Resume Scoring
        </button>
        <button
          type="button"
          className={activeTab === 'match' ? 'input-mode-btn active' : 'input-mode-btn'}
          onClick={() => { setActiveTab('match'); setError(null); }}
        >
          🎯 Job Match & ATS
        </button>
        <button
          type="button"
          className={activeTab === 'history' ? 'input-mode-btn active' : 'input-mode-btn'}
          onClick={() => { setActiveTab('history'); setError(null); }}
        >
          🕒 Analysis History
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
          <div className="match-grid">
            {/* Card 1: Resume */}
            <div className="upload-card">
              <div className="upload-card-header">
                <h3>📄 1. Candidate Resume</h3>
                <span className="upload-badge">Required</span>
              </div>
              <label htmlFor="match-resume-file">Upload Candidate CV (PDF)</label>
              <input
                id="match-resume-file"
                type="file"
                accept="application/pdf"
                onChange={handleMatchFileChange}
                disabled={isLoading}
              />
              {matchFile ? (
                <div className="file-selected-badge">
                  <span>✓ {matchFile.name} ({(matchFile.size / 1024).toFixed(1)} KB)</span>
                  <button
                    type="button"
                    className="file-clear-btn"
                    onClick={() => setMatchFile(null)}
                    title="Remove file"
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <small style={{ color: 'var(--text-muted)' }}>Max file size: 5 MB (PDF format)</small>
              )}
            </div>

            {/* Card 2: Job Description */}
            <div className="upload-card">
              <div className="upload-card-header">
                <h3>🎯 2. Job Description</h3>
                <span className="upload-badge">Required</span>
              </div>

              <div className="input-mode-toggle">
                <button
                  type="button"
                  data-testid="tab-jd-pdf"
                  className={jdInputMode === 'pdf' ? 'input-mode-btn active' : 'input-mode-btn'}
                  onClick={() => setJdInputMode('pdf')}
                >
                  📁 Upload JD (PDF)
                </button>
                <button
                  type="button"
                  data-testid="tab-jd-text"
                  className={jdInputMode === 'text' ? 'input-mode-btn active' : 'input-mode-btn'}
                  onClick={() => setJdInputMode('text')}
                >
                  ✍️ Paste JD Text
                </button>
              </div>

              {jdInputMode === 'pdf' ? (
                <div>
                  <label htmlFor="match-jd-file">Upload Target Job Description (PDF)</label>
                  <input
                    id="match-jd-file"
                    type="file"
                    accept="application/pdf"
                    onChange={handleJdFileChange}
                    disabled={isLoading}
                  />
                  {jdFile ? (
                    <div className="file-selected-badge" style={{ marginTop: '0.5rem' }}>
                      <span>✓ {jdFile.name} ({(jdFile.size / 1024).toFixed(1)} KB)</span>
                      <button
                        type="button"
                        className="file-clear-btn"
                        onClick={() => setJdFile(null)}
                        title="Remove file"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <small style={{ color: 'var(--text-muted)' }}>Upload any PDF job posting (Max: 5 MB)</small>
                  )}
                </div>
              ) : (
                <div>
                  <label htmlFor="job-description">Job Description Text (min 50 chars)</label>
                  <textarea
                    id="job-description"
                    rows={5}
                    placeholder="Paste the target job description or requirements here..."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    disabled={isLoading}
                  />
                  <span
                    className="char-counter"
                    style={{ color: jobDescription.trim().length >= 50 ? 'var(--accent-emerald)' : 'var(--text-muted)' }}
                  >
                    {jobDescription.trim().length >= 50 ? '✓ ' : ''}{jobDescription.trim().length} / 50 characters min
                  </span>
                </div>
              )}
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem', maxWidth: '500px' }}>
            <label htmlFor="target-role">Target Role (Optional title override)</label>
            <input
              id="target-role"
              type="text"
              placeholder="e.g. Senior Backend Engineer"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <button type="submit" disabled={isLoading || !matchFile || !isJdValid}>
            {isLoading ? 'Running Match & ATS Analysis...' : '⚡ Run Job Match & ATS Analysis'}
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