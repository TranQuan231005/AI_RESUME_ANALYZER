import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';
import type { User } from './context/AuthContext';

const user: User = {
  id: 1,
  email: 'user@example.test',
  fullName: 'Demo User',
  role: 'USER',
};

describe('App authenticated flow', () => {
  beforeEach(() => {
    sessionStorage.clear();
    sessionStorage.setItem('accessToken', 'signed-token');
    sessionStorage.setItem('user', JSON.stringify(user));
  });

  test('logout clears the session and redirects a protected route to login', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByRole('heading', { name: 'Resume dashboard' })).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Log out' }));

    expect(screen.getByRole('heading', { name: 'Sign in' })).toBeTruthy();
    expect(sessionStorage.getItem('accessToken')).toBeNull();
    expect(sessionStorage.getItem('user')).toBeNull();
  });
});
