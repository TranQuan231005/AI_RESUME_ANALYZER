import {
  AdminMetricsResponse,
  PagedAdminAnalyses,
  PagedUsers,
} from '../types/analysis';

export const getAdminMetrics = async (
  token: string
): Promise<AdminMetricsResponse> => {
  const response = await fetch('/api/admin/metrics', {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch admin metrics');
  }

  return response.json();
};

export const getAdminUsers = async (
  token: string,
  page = 0,
  size = 10
): Promise<PagedUsers> => {
  const params = new URLSearchParams({ page: String(page), size: String(size) });
  const response = await fetch(`/api/admin/users?${params.toString()}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch admin users');
  }

  return response.json();
};

export const getAdminAnalyses = async (
  token: string,
  page = 0,
  size = 10,
  type?: string,
  provider?: string,
  usedFallback?: boolean
): Promise<PagedAdminAnalyses> => {
  const params = new URLSearchParams({ page: String(page), size: String(size) });
  if (type) params.append('type', type);
  if (provider) params.append('provider', provider);
  if (usedFallback !== undefined) params.append('usedFallback', String(usedFallback));

  const response = await fetch(`/api/admin/analyses?${params.toString()}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch admin analyses');
  }

  return response.json();
};
