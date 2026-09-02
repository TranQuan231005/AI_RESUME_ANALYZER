import {
  PersistedMatchResponse,
  PersistedResumeAnalysisResponse,
  PagedAnalysisSummary,
  AnalysisDetailResponse,
} from '../types/analysis';

export const uploadResume = async (
  file: File,
  token: string
): Promise<PersistedResumeAnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/analyses/resume', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    let errorMessage = 'Failed to upload and analyze resume';
    try {
      const errorData = await response.json();
      if (errorData && errorData.message) {
        errorMessage = Array.isArray(errorData.message)
          ? errorData.message.join(', ')
          : errorData.message;
      }
    } catch {}

    const error = new Error(errorMessage) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }

  return response.json();
};

export const matchJobDescription = async (
  file: File,
  jobDescription: string,
  targetRole: string | undefined,
  token: string
): Promise<PersistedMatchResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('jobDescription', jobDescription);
  if (targetRole) {
    formData.append('targetRole', targetRole);
  }

  const response = await fetch('/api/analyses/match', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    let errorMessage = 'Failed to match resume with job description';
    try {
      const errorData = await response.json();
      if (errorData && errorData.message) {
        errorMessage = Array.isArray(errorData.message)
          ? errorData.message.join(', ')
          : errorData.message;
      }
    } catch {}

    const error = new Error(errorMessage) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }

  return response.json();
};

export const getHistory = async (
  token: string,
  page = 0,
  size = 10,
  type?: string
): Promise<PagedAnalysisSummary> => {
  const params = new URLSearchParams({ page: String(page), size: String(size) });
  if (type) {
    params.append('type', type);
  }

  const response = await fetch(`/api/analyses?${params.toString()}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch analysis history');
  }

  return response.json();
};

export const getAnalysisDetail = async (
  id: number,
  token: string
): Promise<AnalysisDetailResponse> => {
  const response = await fetch(`/api/analyses/${id}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch analysis detail');
  }

  return response.json();
};