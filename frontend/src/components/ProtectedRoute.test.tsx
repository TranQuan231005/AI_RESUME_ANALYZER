import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import * as AuthContext from '../context/AuthContext';

describe('ProtectedRoute Component', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('redirects to /login when token is missing', () => {
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({
      token: null,
      role: null,
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
      role: 'user',
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
});