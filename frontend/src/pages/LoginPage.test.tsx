import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { LoginPage } from './LoginPage';

describe('LoginPage', () => {
  beforeEach(() => {
    sessionStorage.clear();
    global.fetch = jest.fn();
  });

  test('submits credentials and stores the authenticated session', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        accessToken: 'signed-token',
        tokenType: 'Bearer',
        expiresIn: 7200,
        user: {
          id: 1,
          email: 'user@example.test',
          fullName: 'Demo User',
          role: 'USER',
        },
      }),
    });

    render(
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'USER@example.test' },
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'secret-password' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    expect((screen.getByRole('button', { name: 'Signing in…' }) as HTMLButtonElement).disabled).toBe(true);
    await waitFor(() => expect(sessionStorage.getItem('accessToken')).toBe('signed-token'));
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          email: 'USER@example.test',
          password: 'secret-password',
        }),
      }),
    );
  });

  test('shows a safe API error message', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      json: async () => ({ message: 'Invalid email or password.', stackTrace: 'secret' }),
    });

    render(
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'bad@example.test' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrong' } });
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    expect((await screen.findByRole('alert')).textContent).toBe('Invalid email or password.');
    expect(screen.queryByText('secret')).toBeNull();
  });

  test('blocks repeated form submissions and ignores a response after leaving login', async () => {
    let resolve!: (value: unknown) => void;
    (global.fetch as jest.Mock).mockReturnValue(new Promise((done) => { resolve = done; }));
    const { unmount } = render(<MemoryRouter><AuthProvider><LoginPage /></AuthProvider></MemoryRouter>);
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'preview@example.test' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'test-password' } });
    const form = screen.getByRole('button', { name: 'Sign in' }).closest('form')!;
    fireEvent.submit(form);
    fireEvent.submit(form);
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect((screen.getByLabelText('Email') as HTMLInputElement).disabled).toBe(true);
    expect(screen.getByRole('button', { name: /signing in/i }).getAttribute('aria-busy')).toBe('true');
    unmount();
    await act(async () => resolve({ ok: true, json: async () => ({ accessToken: 'late-test-token', user: { id: 1, email: 'preview@example.test', fullName: 'Preview', role: 'USER' } }) }));
    expect(sessionStorage.getItem('accessToken')).toBeNull();
  });
});
