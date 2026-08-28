import type { User } from '../context/AuthContext';

export interface LoginResponse {
  accessToken: string;
  tokenType: 'Bearer';
  expiresIn: number;
  user: User;
}

interface ApiErrorBody {
  message?: unknown;
}

export class ApiRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

export const authenticate = async (email: string, password: string): Promise<LoginResponse> => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    let body: ApiErrorBody = {};
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      // Keep the public error generic when the server response is not valid JSON.
    }
    const message = typeof body.message === 'string' ? body.message : 'Unable to sign in.';
    throw new ApiRequestError(message);
  }

  return (await response.json()) as LoginResponse;
};
