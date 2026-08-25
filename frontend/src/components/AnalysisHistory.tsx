import React from 'react';

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
    return <div data-testid="empty-history">No analysis history found.</div>;
  }

  return (
    <div data-testid="analysis-history">
      <h3>Analysis History</h3>
      <ul>
        {history.map((item) => (
          <li key={item.id} data-testid={`history-item-${item.id}`}>
            <span onClick={() => onSelect(item.id)} data-testid={`select-${item.id}`} style={{ cursor: 'pointer' }}>
              {item.filename} - Score: {item.score} ({item.createdAt})
            </span>
            {onDelete && (
              <button onClick={() => onDelete(item.id)} data-testid={`delete-${item.id}`}>
                Delete
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};