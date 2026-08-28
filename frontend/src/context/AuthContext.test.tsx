import React from 'react';
import { act, renderHook } from '@testing-library/react';
import { AuthProvider, useAuth, type User } from './AuthContext';

const user: User = {
  id: 1,
  email: 'user@example.test',
  fullName: 'Demo User',
  role: 'USER',
};

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('AuthProvider', () => {
  beforeEach(() => sessionStorage.clear());

  test('restores a valid session in the current tab', () => {
    sessionStorage.setItem('accessToken', 'signed-token');
    sessionStorage.setItem('user', JSON.stringify(user));

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.token).toBe('signed-token');
    expect(result.current.user).toEqual(user);
  });

  test.each([
    ['missing token', null, JSON.stringify(user)],
    ['missing user', 'signed-token', null],
    ['malformed JSON', 'signed-token', '{broken'],
    ['invalid role', 'signed-token', JSON.stringify({ ...user, role: 'OWNER' })],
  ])('clears a malformed session: %s', (_name, token, storedUser) => {
    if (token) sessionStorage.setItem('accessToken', token);
    if (storedUser) sessionStorage.setItem('user', storedUser);

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.token).toBeNull();
    expect(result.current.user).toBeNull();
    expect(sessionStorage.getItem('accessToken')).toBeNull();
    expect(sessionStorage.getItem('user')).toBeNull();
  });

  test('login and logout update state and sessionStorage together', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => result.current.login('signed-token', user));
    expect(result.current.token).toBe('signed-token');
    expect(result.current.user).toEqual(user);
    expect(sessionStorage.getItem('accessToken')).toBe('signed-token');
    expect(JSON.parse(sessionStorage.getItem('user') ?? '{}')).toEqual(user);

    act(() => result.current.logout());
    expect(result.current.token).toBeNull();
    expect(result.current.user).toBeNull();
    expect(sessionStorage.length).toBe(0);
  });
});
