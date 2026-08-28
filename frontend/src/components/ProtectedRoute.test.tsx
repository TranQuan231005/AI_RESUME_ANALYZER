import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import * as AuthContext from '../context/AuthContext';

describe('ProtectedRoute Component', () => {
  const user = {
    id: 7,
    email: 'user@example.test',
    fullName: 'Demo User',
    role: 'USER' as const,
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('redirects to /login when token is missing', () => {
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({
      token: null,
      user: null,
      login: jest.fn(),
      logout: jest.fn(),
    });

    const { container } = render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/protected" element={<div>Protected Page</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(container.textContent).toContain('Login Page');
  });

  it('renders outlet when token is present', () => {
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({
      token: 'mock-token',
      user,
      login: jest.fn(),
      logout: jest.fn(),
    });

    const { container } = render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/protected" element={<div>Protected Page</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(container.textContent).toContain('Protected Page');
  });

  it('redirects USER away from the ADMIN route', () => {
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({
      token: 'mock-token',
      user,
      login: jest.fn(),
      logout: jest.fn(),
    });

    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route path="/dashboard" element={<div>User dashboard</div>} />
          <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin" element={<div>Admin dashboard</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('User dashboard')).toBeTruthy();
  });

  it('redirects ADMIN away from the USER route', () => {
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({
      token: 'mock-token',
      user: { ...user, role: 'ADMIN' },
      login: jest.fn(),
      logout: jest.fn(),
    });

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/admin" element={<div>Admin dashboard</div>} />
          <Route element={<ProtectedRoute allowedRoles={['USER']} />}>
            <Route path="/dashboard" element={<div>User dashboard</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Admin dashboard')).toBeTruthy();
  });
});
