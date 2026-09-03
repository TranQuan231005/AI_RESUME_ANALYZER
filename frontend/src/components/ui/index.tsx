import React from 'react';
import { FilePdf, Info, UploadSimple, WarningCircle, X } from '@phosphor-icons/react';
import styles from './ui.module.css';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ variant = 'primary', fullWidth = false, icon, className = '', children, ...props }) => (
  <button className={`${styles.button} ${styles[variant]} ${fullWidth ? styles.fullWidth : ''} ${className}`} {...props}>
    {icon}
    {children}
  </button>
);

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> { label: string; }

export const IconButton: React.FC<IconButtonProps> = ({ label, className = '', children, ...props }) => (
  <button className={`${styles.iconButton} ${className}`} aria-label={label} title={label} {...props}>{children}</button>
);

type BadgeTone = 'neutral' | 'accent' | 'success' | 'warning' | 'danger';

export const Badge: React.FC<{ tone?: BadgeTone; children: React.ReactNode; className?: string }> = ({ tone = 'neutral', children, className = '' }) => (
  <span className={`${styles.badge} ${styles[`badge${tone[0].toUpperCase()}${tone.slice(1)}`]} ${className}`}>{children}</span>
);

interface AlertProps { tone?: 'error' | 'warning' | 'info'; children: React.ReactNode; testId?: string; }

export const Alert: React.FC<AlertProps> = ({ tone = 'info', children, testId }) => {
  const Icon = tone === 'error' ? WarningCircle : Info;
  return (
    <div className={`${styles.alert} ${styles[`alert${tone[0].toUpperCase()}${tone.slice(1)}`]}`} role={tone === 'error' ? 'alert' : 'status'} data-testid={testId}>
      <Icon size={20} weight="bold" aria-hidden="true" />
      <div>{children}</div>
    </div>
  );
};

export interface SegmentOption<T extends string> { value: T; label: string; icon?: React.ReactNode; testId?: string; }

interface SegmentedControlProps<T extends string> {
  value: T;
  options: SegmentOption<T>[];
  onChange: (value: T) => void;
  label: string;
}

export function SegmentedControl<T extends string>({ value, options, onChange, label }: SegmentedControlProps<T>) {
  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>, index: number) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let nextIndex = index;
    if (event.key === 'ArrowRight') nextIndex = (index + 1) % options.length;
    if (event.key === 'ArrowLeft') nextIndex = (index - 1 + options.length) % options.length;
    if (event.key === 'Home') nextIndex = 0;
    if (event.key === 'End') nextIndex = options.length - 1;
    onChange(options[nextIndex].value);
    const group = event.currentTarget.parentElement;
    (group?.children[nextIndex] as HTMLButtonElement | undefined)?.focus();
  };

  return (
    <div className={styles.segments} role="group" aria-label={label}>
      {options.map((option, index) => (
        <button
          key={option.value}
          type="button"
          data-testid={option.testId}
          className={`${styles.segment} ${option.value === value ? styles.segmentActive : ''}`}
          aria-pressed={option.value === value}
          onClick={() => onChange(option.value)}
          onKeyDown={(event) => handleKeyDown(event, index)}
        >
          {option.icon}{option.label}
        </button>
      ))}
    </div>
  );
}

interface FileDropzoneProps {
  id: string;
  label: string;
  file: File | null;
  accept?: string;
  disabled?: boolean;
  helperText: string;
  onChange: (file: File | null) => void;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({ id, label, file, accept = 'application/pdf', disabled = false, helperText, onChange }) => {
  const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => onChange(event.target.files?.[0] ?? null);
  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (!disabled) onChange(event.dataTransfer.files?.[0] ?? null);
  };

  return (
    <div className={`${styles.dropzone} ${file ? styles.dropzoneSelected : ''} ${disabled ? styles.dropzoneDisabled : ''}`} onDragOver={(event) => event.preventDefault()} onDrop={handleDrop}>
      <input id={id} className="sr-only" type="file" accept={accept} disabled={disabled} onChange={handleInput} />
      {file ? (
        <div className={styles.fileRow}>
          <label className="sr-only" htmlFor={id}>{label}</label>
          <span className={styles.dropIcon}><FilePdf size={24} weight="duotone" aria-hidden="true" /></span>
          <span>
            <span className={styles.fileName}>{file.name}</span>
            <span className={styles.fileMeta}>{(file.size / 1024).toFixed(1)} KB</span>
          </span>
          <IconButton type="button" label={`Remove ${file.name}`} onClick={(event) => { event.preventDefault(); onChange(null); }}>
            <X size={18} weight="bold" aria-hidden="true" />
          </IconButton>
        </div>
      ) : (
        <label className={styles.dropPrompt} htmlFor={id}>
          <span className={styles.dropIcon}><UploadSimple size={24} weight="bold" aria-hidden="true" /></span>
          <span className={styles.dropCopy}><strong>{label}</strong><span>{helperText}</span></span>
        </label>
      )}
    </div>
  );
};

interface PageHeaderProps { eyebrow?: string; title: string; description: string; }

export const PageHeader: React.FC<PageHeaderProps> = ({ eyebrow, title, description }) => (
  <header className={styles.pageHeader}>
    {eyebrow && <p className={styles.eyebrow}>{eyebrow}</p>}
    <h1>{title}</h1>
    <p>{description}</p>
  </header>
);

interface EmptyStateProps { title: string; description: string; action?: React.ReactNode; testId?: string; }

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description, action, testId }) => (
  <div className={styles.emptyState} data-testid={testId}>
    <h2>{title}</h2><p>{description}</p>{action}
  </div>
);

export const LoadingSkeleton: React.FC<{ label: string; testId?: string }> = ({ label, testId }) => (
  <div className={styles.skeleton} role="status" data-testid={testId} aria-label={label}>
    <span className={styles.skeletonLine} /><span className={styles.skeletonLine} /><span className={styles.skeletonLine} />
    <span className="sr-only">{label}</span>
  </div>
);

interface ScoreSummaryProps { score: number; label: string; hint: string; }

export const ScoreSummary: React.FC<ScoreSummaryProps> = ({ score, label, hint }) => (
  <section className={styles.score} aria-label={`${label} ${score} out of 100`}>
    <div className={styles.scoreCopy}>
      <h3>{label}: {score}/100</h3>
      <span className={styles.scoreNumber}>{score}<small>/100</small></span>
    </div>
    <div>
      <meter className={styles.meter} min={0} max={100} value={score} aria-label={label} />
      <p className={styles.scoreHint}>{hint}</p>
    </div>
  </section>
);
