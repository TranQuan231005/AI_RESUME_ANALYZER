import React from 'react';
import { Link } from 'react-router-dom';

export const ResumeResultPage: React.FC = () => (
  <section>
    <h1>Resume analysis result</h1>
    <p>No analysis result is available.</p>
    <Link to="/dashboard">Return to dashboard</Link>
  </section>
);
