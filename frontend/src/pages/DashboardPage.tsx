import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { uploadResume } from '../api/analysis';

export const DashboardPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const { token, logout } = useAuth();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        setError('Please select a valid PDF file.');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a PDF file before submitting.');
      return;
    }

    if (!token) {
      setError('Authentication token is missing. Please log in again.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await uploadResume(file, token);
      navigate('/resume/result', { state: { result } });
    } catch (err: any) {
      if (err?.status === 401) {
        if (logout) {
          logout();
        }
        navigate('/login');
        return;
      }
      setError(err?.message || 'Failed to upload resume. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section>
      <h1>Resume dashboard</h1>
      <p>Analyze a resume and review your previous results.</p>
      <Link to="/resume/result">View latest result</Link>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="resume-file">Upload Resume (PDF)</label>
          <input
            id="resume-file"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            disabled={isLoading}
          />
        </div>

        {error && <p role="alert">{error}</p>}

        <button type="submit" disabled={isLoading || !file}>
          {isLoading ? 'Uploading...' : 'Upload Resume'}
        </button>
      </form>
    </section>
  );
};