import React, { useEffect, useState } from 'react';
import { ChartDonut, Clock, FileText, Gauge, Target, Users } from '@phosphor-icons/react';
import { useAuth } from '../context/AuthContext';
import { getAdminMetrics, getAdminUsers, getAdminAnalyses } from '../api/admin';
import { Alert, Badge, LoadingSkeleton, PageHeader } from '../components/ui';
import type {
  AdminMetricsResponse,
  PagedUsers,
  PagedAdminAnalyses,
} from '../types/analysis';
import styles from './AdminPage.module.css';

export const AdminPage: React.FC = () => {
  const { token, user } = useAuth();
  const [metrics, setMetrics] = useState<AdminMetricsResponse | null>(null);
  const [users, setUsers] = useState<PagedUsers | null>(null);
  const [analyses, setAnalyses] = useState<PagedAdminAnalyses | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    const fetchAdminData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [metricsData, usersData, analysesData] = await Promise.all([
          getAdminMetrics(token),
          getAdminUsers(token, 0, 10),
          getAdminAnalyses(token, 0, 10),
        ]);
        setMetrics(metricsData);
        setUsers(usersData);
        setAnalyses(analysesData);
      } catch (err: any) {
        setError(err.message || 'Failed to load admin data');
      } finally {
        setLoading(false);
      }
    };

    fetchAdminData();
  }, [token]);

  return (
    <section className={styles.page} data-testid="admin-page">
      <PageHeader eyebrow="System overview" title="Admin dashboard" description="Review analysis activity, model behavior, and the health of the local AI workflow." />

      {loading && <LoadingSkeleton label="Loading admin metrics..." />}
      {error && <Alert tone="error">{error}</Alert>}

      {metrics && (
        <section data-testid="admin-metrics-section">
          <h2 className="sr-only">System Performance & AI Telemetry</h2>
          <div className={styles.metrics}>
            <div className={styles.metric}><ChartDonut className={styles.metricIcon} size={21} weight="bold" aria-hidden="true" /><h3>Total Analyses</h3><p>{metrics.totalAnalyses}</p></div>
            <div className={styles.metric}><FileText className={styles.metricIcon} size={21} weight="bold" aria-hidden="true" /><h3>Resume Analyses</h3><p>{metrics.resumeAnalysesCount}</p></div>
            <div className={styles.metric}><Target className={styles.metricIcon} size={21} weight="bold" aria-hidden="true" /><h3>Match Analyses</h3><p>{metrics.matchAnalysesCount}</p></div>
            <div className={styles.metric}><Gauge className={styles.metricIcon} size={21} weight="bold" aria-hidden="true" /><h3>Fallback Rate</h3><p>{(metrics.fallbackRate * 100).toFixed(1)}%</p></div>
            <div className={styles.metric}><Clock className={styles.metricIcon} size={21} weight="bold" aria-hidden="true" /><h3>Avg Processing Time</h3><p>{metrics.avgLatencyMs} ms</p></div>
            <div className={styles.metric}><Clock className={styles.metricIcon} size={21} weight="bold" aria-hidden="true" /><h3>P95 Latency</h3><p>{metrics.p95LatencyMs} ms</p></div>
          </div>
        </section>
      )}

      {users && (
        <section className={styles.dataSection} data-testid="admin-users-section">
          <div className={styles.sectionHeader}><h2>Registered Users</h2><Badge tone="neutral"><Users size={14} weight="bold" aria-hidden="true" />{users.totalItems} total</Badge></div>
          <div className={styles.tableWrap} role="region" aria-label="Registered users table" tabIndex={0}><table className={styles.table}>
            <caption className="sr-only">Registered users</caption>
            <thead>
              <tr>
                <th className={styles.numeric}>ID</th><th>Email</th><th>Full Name</th><th>Role</th>
              </tr>
            </thead>
            <tbody>
              {users.items.map((u) => (
                <tr key={u.id}>
                  <td className={styles.numeric}>{u.id}</td><td className={styles.primaryCell}>{u.email}</td><td>{u.fullName}</td><td><Badge tone={u.role === 'ADMIN' ? 'accent' : 'neutral'}>{u.role}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table></div>
        </section>
      )}

      {analyses && (
        <section className={styles.dataSection} data-testid="admin-analyses-section">
          <div className={styles.sectionHeader}><h2>Recent Analyses</h2><Badge tone="neutral">{analyses.totalItems} total</Badge></div>
          <div className={styles.tableWrap} role="region" aria-label="Recent analyses table" tabIndex={0}><table className={`${styles.table} ${styles.tableWide}`}>
            <caption className="sr-only">Recent analyses</caption>
            <thead>
              <tr>
                <th className={styles.numeric}>ID</th><th>Type</th><th>File</th><th className={styles.numeric}>Score</th><th>Provider</th><th>Fallback</th><th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {analyses.items.map((a) => (
                <tr key={a.id}>
                  <td className={styles.numeric}>{a.id}</td><td><Badge tone={a.analysisType === 'RESUME' ? 'accent' : 'neutral'}>{a.analysisType}</Badge></td><td className={styles.primaryCell}>{a.fileName}</td><td className={styles.numeric}>{a.resumeScore ?? a.matchScore ?? '-'}</td><td>{a.aiProvider}</td><td><Badge tone={a.usedFallback ? 'warning' : 'success'}>{a.usedFallback ? 'Yes' : 'No'}</Badge></td><td>{new Date(a.createdAt).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table></div>
        </section>
      )}
    </section>
  );
};
