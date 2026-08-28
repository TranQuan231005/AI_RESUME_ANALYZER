import React from 'react';
import { Link } from 'react-router-dom';

export const ForbiddenPage: React.FC = () => (
  <main>
    <h1>Access denied</h1>
    <p>Your account does not have permission to view this page.</p>
    <Link to="/">Return home</Link>
  </main>
);
