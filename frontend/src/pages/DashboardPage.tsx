import React from 'react';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => (
  <section>
    <h1>Resume dashboard</h1>
    <p>Analyze a resume and review your previous results.</p>
    <Link to="/resume/result">View latest result</Link>
  </section>
);
