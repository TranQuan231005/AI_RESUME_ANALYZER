import React from 'react';
import { Trash } from '@phosphor-icons/react';
import { Button, EmptyState } from './ui';
import styles from './AnalysisHistory.module.css';

export interface HistoryItem {
  id: string;
  filename: string;
  score: number;
  createdAt: string;
}

interface AnalysisHistoryProps {
  history: HistoryItem[];
  onSelect: (id: string) => void;
  onDelete?: (id: string) => void;
}

export const AnalysisHistory: React.FC<AnalysisHistoryProps> = ({ history, onSelect, onDelete }) => {
  if (!history || history.length === 0) {
    return <EmptyState testId="empty-history" title="No analysis history found." description="Your completed analyses will appear here." />;
  }

  return (
    <div className={styles.history} data-testid="analysis-history">
      <h3>Analysis History</h3>
      <ul className={styles.list}>
        {history.map((item) => (
          <li className={styles.item} key={item.id} data-testid={`history-item-${item.id}`}>
            <button type="button" className={styles.select} onClick={() => onSelect(item.id)} data-testid={`select-${item.id}`}>
              {item.filename} - Score: {item.score} ({item.createdAt})
            </button>
            {onDelete && (
              <Button type="button" variant="danger" icon={<Trash size={17} weight="bold" aria-hidden="true" />} onClick={() => onDelete(item.id)} data-testid={`delete-${item.id}`}>Delete</Button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};
