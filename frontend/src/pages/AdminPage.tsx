import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getAdminMetrics, getAdminUsers, getAdminAnalyses } from '../api/admin';
import type {
  AdminMetricsResponse,
  PagedUsers,
  PagedAdminAnalyses,
} from '../types/analysis';

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
    <section data-testid="admin-page">
      <h1>Admin dashboard</h1>
      <p>Review system activity and service health.</p>

      {loading && <p role="status">Loading admin metrics...</p>}
      {error && <p role="alert" style={{ color: 'red' }}>{error}</p>}

      {metrics && (
        <section data-testid="admin-metrics-section">
          <h2>System Performance & AI Telemetry</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h3>Total Analyses</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{metrics.totalAnalyses}</p>
            </div>
            <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h3>Resume Analyses</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{metrics.resumeAnalysesCount}</p>
            </div>
            <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h3>Match Analyses</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{metrics.matchAnalysesCount}</p>
            </div>
            <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h3>Fallback Rate</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{(metrics.fallbackRate * 100).toFixed(1)}%</p>
            </div>
            <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h3>Avg Processing Time</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{metrics.avgLatencyMs} ms</p>
            </div>
            <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h3>P95 Latency</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{metrics.p95LatencyMs} ms</p>
            </div>
          </div>
        </section>
      )}

      {users && (
        <section data-testid="admin-users-section" style={{ marginTop: '2rem' }}>
          <h2>Registered Users ({users.totalItems})</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '0.5rem' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ddd', textAlign: 'left' }}>
                <th style={{ padding: '8px' }}>ID</th>
                <th style={{ padding: '8px' }}>Email</th>
                <th style={{ padding: '8px' }}>Full Name</th>
                <th style={{ padding: '8px' }}>Role</th>
              </tr>
            </thead>
            <tbody>
              {users.items.map((u) => (
                <tr key={u.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px' }}>{u.id}</td>
                  <td style={{ padding: '8px' }}>{u.email}</td>
                  <td style={{ padding: '8px' }}>{u.fullName}</td>
                  <td style={{ padding: '8px' }}>{u.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {analyses && (
        <section data-testid="admin-analyses-section" style={{ marginTop: '2rem' }}>
          <h2>Recent Analyses ({analyses.totalItems})</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '0.5rem' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ddd', textAlign: 'left' }}>
                <th style={{ padding: '8px' }}>ID</th>
                <th style={{ padding: '8px' }}>Type</th>
                <th style={{ padding: '8px' }}>File</th>
                <th style={{ padding: '8px' }}>Score</th>
                <th style={{ padding: '8px' }}>Provider</th>
                <th style={{ padding: '8px' }}>Fallback</th>
                <th style={{ padding: '8px' }}>Created At</th>
              </tr>
            </thead>
            <tbody>
              {analyses.items.map((a) => (
                <tr key={a.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px' }}>{a.id}</td>
                  <td style={{ padding: '8px' }}>{a.analysisType}</td>
                  <td style={{ padding: '8px' }}>{a.fileName}</td>
                  <td style={{ padding: '8px' }}>{a.resumeScore ?? a.matchScore ?? '-'}</td>
                  <td style={{ padding: '8px' }}>{a.aiProvider}</td>
                  <td style={{ padding: '8px' }}>{a.usedFallback ? 'Yes' : 'No'}</td>
                  <td style={{ padding: '8px' }}>{new Date(a.createdAt).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </section>
  );
};
