import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const AppShell: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div>
      <header>
        <Link to={user?.role === 'ADMIN' ? '/admin' : '/dashboard'}>AI Resume Analyzer</Link>
        <nav aria-label="Account navigation">
          <span>{user?.fullName}</span>
          <button type="button" onClick={logout}>Log out</button>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
};
