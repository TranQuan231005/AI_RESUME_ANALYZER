import { useLayoutEffect, useRef, useState } from 'react';
import type { ProgressStatus } from './useSimulatedProgress';

export function useAnalysisAction(token: string | null) {
  const [resumePending, setResumePending] = useState(false);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [matchStatus, setMatchStatus] = useState<ProgressStatus>('idle');
  const [matchError, setMatchError] = useState<string | null>(null);
  const locked = useRef(false);
  const generation = useRef(0);
  const completionTimer = useRef<number>();

  useLayoutEffect(() => {
    locked.current = false;
    setResumePending(false);
    setResumeError(null);
    setMatchStatus('idle');
    setMatchError(null);
    return () => {
      generation.current += 1;
      window.clearTimeout(completionTimer.current);
    };
  }, [token]);

  async function run<T>(kind: 'resume' | 'match', request: () => Promise<T>, onSuccess: (value: T) => void, onUnauthorized: () => void) {
    if (locked.current || !token) return;
    locked.current = true;
    const current = ++generation.current;
    setResumeError(null);
    setMatchError(null);
    if (kind === 'resume') setResumePending(true);
    else setMatchStatus('pending');

    const release = () => {
      locked.current = false;
      setResumePending(false);
    };
    try {
      const response = await request();
      if (generation.current !== current) return;
      if (kind === 'match') {
        setMatchStatus('success');
        completionTimer.current = window.setTimeout(() => {
          if (generation.current !== current) return;
          release();
          setMatchStatus('idle');
          onSuccess(response);
        }, 400);
      } else {
        release();
        onSuccess(response);
      }
    } catch (caught) {
      if (generation.current !== current) return;
      release();
      if ((caught as { status?: number } | null)?.status === 401) {
        setMatchStatus('idle');
        onUnauthorized();
        return;
      }
      const message = caught instanceof Error ? caught.message : 'Unable to complete analysis. Please try again.';
      if (kind === 'match') {
        setMatchError(message);
        setMatchStatus('error');
      } else setResumeError(message);
    }
  }

  return {
    run, resumePending, resumeError, matchStatus, matchError,
    busy: resumePending || matchStatus === 'pending' || matchStatus === 'success',
    clearResumeError: () => setResumeError(null),
    closeMatchError: () => { setMatchStatus('idle'); setMatchError(null); },
  };
}
