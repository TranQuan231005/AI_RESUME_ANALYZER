import { useEffect, useState } from 'react';

export type ProgressStatus = 'idle' | 'pending' | 'success' | 'error';

// This is a waiting animation, not measured server progress.
export function useSimulatedProgress(status: ProgressStatus) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    if (status !== 'pending') return;
    setElapsed(0);
    const started = performance.now();
    const timer = window.setInterval(() => setElapsed(performance.now() - started), 250);
    return () => window.clearInterval(timer);
  }, [status]);

  const seconds = elapsed / 1000;
  const estimate = seconds <= 10 ? seconds * 6.5
    : seconds <= 30 ? 65 + (seconds - 10)
    : 85 + Math.min(30, seconds - 30) / 3;
  return {
    percent: status === 'success' ? 100 : Math.min(95, Math.floor(estimate)),
    canMinimize: seconds >= 60,
    message: seconds >= 60 ? 'This is taking a little longer. Your analysis is still running.'
      : ['A little patience, a clearer picture.', 'Good things take a moment.', 'Your next opportunity is worth the wait.'][Math.floor(seconds / 8) % 3],
  };
}
