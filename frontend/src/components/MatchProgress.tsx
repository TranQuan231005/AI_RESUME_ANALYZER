import React, { useEffect, useId, useRef } from 'react';
import { CheckCircle, FileText, Sparkle, WarningCircle } from '@phosphor-icons/react';
import { Button } from './ui';
import { ProgressStatus, useSimulatedProgress } from '../hooks/useSimulatedProgress';
import styles from './MatchProgress.module.css';

interface MatchProgressProps {
  status: ProgressStatus;
  error: string | null;
  minimized: boolean;
  onMinimize: () => void;
  onExpand: () => void;
  onClose: () => void;
  onRetry: () => void;
}

export function MatchProgress({ status, error, minimized, onMinimize, onExpand, onClose, onRetry }: MatchProgressProps) {
  const progress = useSimulatedProgress(status);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const inlineRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const descriptionId = useId();
  const modal = status !== 'idle' && !minimized;

  useEffect(() => {
    if (!modal) return;
    const dialog = dialogRef.current!;
    const previousFocus = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    dialog.showModal();
    document.body.style.overflow = 'hidden';
    titleRef.current?.focus();
    return () => {
      dialog.close();
      document.body.style.overflow = previousOverflow;
      if (previousFocus?.isConnected) previousFocus.focus();
    };
  }, [modal]);

  useEffect(() => {
    if (minimized) inlineRef.current?.focus();
  }, [minimized]);

  if (status === 'idle') return null;
  const failed = status === 'error';
  const complete = status === 'success';
  const title = failed ? 'Your match could not finish' : complete ? 'Your results are ready' : 'Finding your fit';
  const message = failed ? error : complete ? 'Opening your match report...' : progress.message;
  const content = (
    <>
      <div className={`${styles.illustration} ${status === 'pending' ? styles.scanning : ''}`} aria-hidden="true">
        {failed ? <WarningCircle size={72} weight="duotone" /> : complete ? <CheckCircle size={72} weight="duotone" /> : (
          <><FileText size={84} weight="duotone" /><span className={styles.scanLine} /><Sparkle className={styles.sparkle} size={24} weight="fill" /></>
        )}
      </div>
      <h2 id={titleId} ref={titleRef} tabIndex={-1}>{title}</h2>
      <p id={descriptionId} role={failed ? 'alert' : 'status'} className={styles.message}>{message}</p>
      {!failed && (
        <div className={styles.progressGroup}>
          <div className={styles.progressLabel}><span>{complete ? 'Complete' : 'Estimated progress'}</span><strong aria-hidden="true">{progress.percent}%</strong></div>
          <progress max={100} value={progress.percent} aria-label="Estimated match progress" />
          {!complete && <span className={styles.waiting} aria-hidden="true"><i /><i /><i /></span>}
        </div>
      )}
      <div className={styles.actions}>
        {failed ? <><Button type="button" variant="secondary" onClick={onClose}>Close</Button><Button type="button" onClick={onRetry}>Try again</Button></>
          : !complete && (minimized ? <Button type="button" variant="secondary" onClick={onExpand}>Show progress</Button>
            : progress.canMinimize && <Button type="button" variant="ghost" onClick={onMinimize}>Minimize</Button>)}
      </div>
    </>
  );

  if (minimized) return <div ref={inlineRef} tabIndex={-1} className={styles.inline} aria-labelledby={titleId}>{content}</div>;
  return (
    <dialog ref={dialogRef} className={styles.dialog} aria-labelledby={titleId} aria-describedby={descriptionId}
      onCancel={(event) => { event.preventDefault(); if (failed) onClose(); }}>
      {content}
    </dialog>
  );
}
