import React, { createContext, useContext, useMemo, useState } from 'react';

export type UserRole = 'USER' | 'ADMIN';

export interface User {
  id: number;
  email: string;
  fullName: string;
  role: UserRole;
}

export interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (accessToken: string, user: User) => void;
  logout: () => void;
}

const ACCESS_TOKEN_KEY = 'accessToken';
const USER_KEY = 'user';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const isUser = (value: unknown): value is User => {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.id === 'number' &&
    Number.isSafeInteger(candidate.id) &&
    candidate.id > 0 &&
    typeof candidate.email === 'string' &&
    typeof candidate.fullName === 'string' &&
    (candidate.role === 'USER' || candidate.role === 'ADMIN')
  );
};

const clearStoredSession = () => {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
};

const readStoredSession = (): Pick<AuthContextType, 'token' | 'user'> => {
  const token = sessionStorage.getItem(ACCESS_TOKEN_KEY);
  const storedUser = sessionStorage.getItem(USER_KEY);

  if (!token || !storedUser) {
    clearStoredSession();
    return { token: null, user: null };
  }

  try {
    const user: unknown = JSON.parse(storedUser);
    if (!isUser(user)) throw new Error('Invalid session user');
    return { token, user };
  } catch {
    clearStoredSession();
    return { token: null, user: null };
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState(readStoredSession);

  const value = useMemo<AuthContextType>(
    () => ({
      ...session,
      login: (accessToken, user) => {
        sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
        sessionStorage.setItem(USER_KEY, JSON.stringify(user));
        setSession({ token: accessToken, user });
      },
      logout: () => {
        clearStoredSession();
        setSession({ token: null, user: null });
      },
    }),
    [session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
