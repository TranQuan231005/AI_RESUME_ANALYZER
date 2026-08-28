import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { AdminPage } from './pages/AdminPage';
import { DashboardPage } from './pages/DashboardPage';
import { ForbiddenPage } from './pages/ForbiddenPage';
import { LoginPage } from './pages/LoginPage';
import { ResumeResultPage } from './pages/ResumeResultPage';

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forbidden" element={<ForbiddenPage />} />
        <Route element={<AppShell />}>
          <Route element={<ProtectedRoute allowedRoles={['USER']} />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/resume/result" element={<ResumeResultPage />} />
          </Route>
          <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin" element={<AdminPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
