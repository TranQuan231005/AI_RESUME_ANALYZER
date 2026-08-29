import { ResumeAnalysisResult } from '../types/analysis';

export const uploadResume = async (
  file: File,
  token: string
): Promise<ResumeAnalysisResult> => {
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
    } catch 
    {
    }

    const error = new Error(errorMessage) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }

  return response.json();
};