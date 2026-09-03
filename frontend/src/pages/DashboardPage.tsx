import React, { useEffect, useState } from 'react';
import {
  ArrowRight,
  ChartDonut,
  ClockCounterClockwise,
  FileText,
  Target,
  TextAlignLeft,
} from '@phosphor-icons/react';
import { useNavigate } from 'react-router-dom';
import { getHistory, matchJobDescription, uploadResume } from '../api/analysis';
import { Alert, Badge, Button, EmptyState, FileDropzone, LoadingSkeleton, PageHeader, SegmentedControl } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import type { PagedAnalysisSummary } from '../types/analysis';
import styles from './DashboardPage.module.css';

type DashboardTab = 'resume' | 'match' | 'history';
type JdInputMode = 'pdf' | 'text';

const isPdf = (file: File) => file.type === 'application/pdf';
const MAX_FILE_SIZE = 5 * 1024 * 1024;

export const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<DashboardTab>('resume');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [matchFile, setMatchFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdInputMode, setJdInputMode] = useState<JdInputMode>('pdf');
  const [jobDescription, setJobDescription] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [history, setHistory] = useState<PagedAnalysisSummary | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { token, logout } = useAuth();

  const loadHistory = async () => {
    if (!token) return;
    setHistoryLoading(true);
    setError(null);
    try {
      setHistory(await getHistory(token, 0, 10));
    } catch (err: any) {
      setError(err?.message || 'Failed to load history.');
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'history' && token) void loadHistory();
  }, [activeTab, token]);

  const choosePdf = (file: File | null, setter: React.Dispatch<React.SetStateAction<File | null>>, message: string) => {
    if (file && !isPdf(file)) {
      setter(null);
      setError(message);
      return;
    }
    if (file && file.size > MAX_FILE_SIZE) {
      setter(null);
      setError('PDF files must be 5 MB or smaller.');
      return;
    }
    setter(file);
    setError(null);
  };

  const handleResumeSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!resumeFile) return setError('Please select a PDF file before submitting.');
    if (!token) return setError('Authentication token is missing. Please log in again.');
    setIsLoading(true);
    setError(null);
    try {
      const response = await uploadResume(resumeFile, token);
      navigate('/resume/result', { state: { result: (response as any).result || response } });
    } catch (err: any) {
      if (err?.status === 401) {
        logout();
        navigate('/login');
        return;
      }
      setError(err?.message || 'Failed to upload resume. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const isJdValid = jdInputMode === 'pdf' ? Boolean(jdFile) : jobDescription.trim().length >= 50;

  const handleMatchSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!matchFile) return setError('Please select a Candidate Resume PDF file before submitting.');
    if (jdInputMode === 'pdf' && !jdFile) return setError('Please select a Job Description PDF file.');
    if (jdInputMode === 'text' && jobDescription.trim().length < 50) return setError('Job description must be at least 50 characters.');
    if (!token) return setError('Authentication token is missing. Please log in again.');
    setIsLoading(true);
    setError(null);
    try {
      const response = await matchJobDescription(
        matchFile,
        jdInputMode === 'text' ? jobDescription : undefined,
        targetRole.trim() || undefined,
        token,
        jdInputMode === 'pdf' ? jdFile : null,
      );
      navigate('/match/result', { state: { result: (response as any).result || response } });
    } catch (err: any) {
      if (err?.status === 401) {
        logout();
        navigate('/login');
        return;
      }
      setError(err?.message || 'Failed to match resume with job description.');
    } finally {
      setIsLoading(false);
    }
  };

  const selectTab = (tab: DashboardTab) => {
    setActiveTab(tab);
    setError(null);
  };

  return (
    <section className={styles.page}>
      <PageHeader eyebrow="Analysis workspace" title="Resume dashboard" description="Score a resume, compare it with a role, or revisit your previous analyses." />

      <div className={styles.toolbar}>
        <SegmentedControl
          label="Analysis workspace"
          value={activeTab}
          onChange={selectTab}
          options={[
            { value: 'resume', label: 'Resume Scoring', icon: <ChartDonut size={18} weight="bold" aria-hidden="true" /> },
            { value: 'match', label: 'Job Match & ATS', icon: <Target size={18} weight="bold" aria-hidden="true" /> },
            { value: 'history', label: 'Analysis History', icon: <ClockCounterClockwise size={18} weight="bold" aria-hidden="true" /> },
          ]}
        />
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      {activeTab === 'resume' && (
        <form className={styles.workspace} onSubmit={handleResumeSubmit}>
          <div className={styles.panel}>
            <div className={styles.panelHeader}>
              <h2>Start with your resume.</h2>
              <p>Upload an English, text-based PDF to receive a structured quality score and focused recommendations.</p>
            </div>
            <FileDropzone
              id="resume-file"
              label="Upload Resume (PDF)"
              file={resumeFile}
              disabled={isLoading}
              helperText="Drop a PDF here or click to browse. Maximum size: 5 MB."
              onChange={(file) => choosePdf(file, setResumeFile, 'Please select a valid PDF file.')}
            />
            <div className={styles.actionRow}>
              <Button type="submit" disabled={isLoading || !resumeFile} icon={<ArrowRight size={18} weight="bold" aria-hidden="true" />}>
                {isLoading ? 'Uploading...' : 'Upload Resume'}
              </Button>
            </div>
          </div>
          <aside className={styles.aside}>
            <FileText className={styles.asideIcon} size={34} weight="duotone" aria-hidden="true" />
            <div>
              <h3>Your document stays private.</h3>
              <p>The original resume is processed in memory and is not stored after analysis.</p>
            </div>
          </aside>
        </form>
      )}

      {activeTab === 'match' && (
        <form className={styles.panel} onSubmit={handleMatchSubmit} data-testid="match-form">
          <div className={styles.panelHeader}>
            <h2>Compare experience with opportunity.</h2>
            <p>Bring a resume and a job description together to reveal matched skills, gaps, and ATS keywords.</p>
          </div>
          <div className={styles.matchGrid}>
            <section className={styles.matchColumn}>
              <div className={styles.columnHeader}><h3>Candidate resume</h3><Badge tone="accent">Required</Badge></div>
              <FileDropzone
                id="match-resume-file"
                label="Upload Candidate CV (PDF)"
                file={matchFile}
                disabled={isLoading}
                helperText="English PDF, maximum size 5 MB."
                onChange={(file) => choosePdf(file, setMatchFile, 'Please select a valid PDF file for Candidate Resume.')}
              />
            </section>

            <section className={styles.matchColumn}>
              <div className={styles.columnHeader}><h3>Job description</h3><Badge tone="accent">Required</Badge></div>
              <SegmentedControl
                label="Job description input mode"
                value={jdInputMode}
                onChange={setJdInputMode}
                options={[
                  { value: 'pdf', label: 'Upload JD (PDF)', icon: <FileText size={17} weight="bold" aria-hidden="true" />, testId: 'tab-jd-pdf' },
                  { value: 'text', label: 'Paste JD Text', icon: <TextAlignLeft size={17} weight="bold" aria-hidden="true" />, testId: 'tab-jd-text' },
                ]}
              />
              {jdInputMode === 'pdf' ? (
                <FileDropzone
                  id="match-jd-file"
                  label="Upload Target Job Description (PDF)"
                  file={jdFile}
                  disabled={isLoading}
                  helperText="Any text-based job posting PDF, maximum size 5 MB."
                  onChange={(file) => choosePdf(file, setJdFile, 'Please select a valid PDF file for Job Description.')}
                />
              ) : (
                <div className={styles.field}>
                  <label htmlFor="job-description">Job Description Text (min 50 chars)</label>
                  <textarea id="job-description" rows={7} placeholder="Paste the target job description or requirements here..." value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} disabled={isLoading} />
                  <span className={`${styles.counter} ${jobDescription.trim().length >= 50 ? styles.counterValid : ''}`}>
                    {jobDescription.trim().length} / 50 characters minimum
                  </span>
                </div>
              )}
            </section>
          </div>
          <div className={`${styles.field} ${styles.targetRole}`}>
            <label htmlFor="target-role">Target Role (Optional title override)</label>
            <input id="target-role" type="text" placeholder="e.g. Senior Backend Engineer" value={targetRole} onChange={(event) => setTargetRole(event.target.value)} disabled={isLoading} />
          </div>
          <div className={styles.actionRow}>
            <Button type="submit" disabled={isLoading || !matchFile || !isJdValid} icon={<Target size={18} weight="bold" aria-hidden="true" />}>
              {isLoading ? 'Running Match & ATS Analysis...' : 'Run Job Match & ATS Analysis'}
            </Button>
          </div>
        </form>
      )}

      {activeTab === 'history' && (
        <section className={styles.panel} data-testid="history-tab">
          <div className={styles.panelHeader}><h2>Your Analysis History</h2><p>A concise record of the latest resume and job-match analyses.</p></div>
          {historyLoading && <LoadingSkeleton label="Loading history..." />}
          {!historyLoading && history && history.items.length === 0 && <EmptyState title="No previous analyses found." description="Run your first resume score or job match to build a history." />}
          {!historyLoading && history && history.items.length > 0 && (
            <ul className={styles.history}>
              {history.items.map((item) => (
                <li className={styles.historyItem} key={item.id}>
                  <Badge tone={item.analysisType === 'RESUME' ? 'accent' : 'neutral'}>{item.analysisType}</Badge>
                  <span className={styles.historyName}><strong>{item.fileName}</strong><span>{item.aiProvider}{item.usedFallback ? ' / fallback' : ''}</span></span>
                  <span className={styles.historyScore}>{item.analysisType === 'RESUME' ? `Score ${item.resumeScore}/100` : `Match ${item.matchScore}/100`}</span>
                  <time className={styles.historyDate}>{new Date(item.createdAt).toLocaleDateString()}</time>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </section>
  );
};
