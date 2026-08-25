import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { describe, test, expect, jest } from '@jest/globals';
import { AnalysisHistory, HistoryItem } from './AnalysisHistory';

describe('AnalysisHistory Component', () => {
  const mockHistory: HistoryItem[] = [
    { id: '1', filename: 'CV_John_Doe.pdf', score: 85, createdAt: '2026-08-25' },
    { id: '2', filename: 'CV_Jane_Smith.pdf', score: 90, createdAt: '2026-08-24' },
  ];

  test('renders empty state when no history items', () => {
    const { getByTestId } = render(<AnalysisHistory history={[]} onSelect={() => {}} />);
    expect(getByTestId('empty-history')).toBeTruthy();
  });

  test('renders history items list and handles select event', () => {
    const handleSelect = jest.fn();
    const { getByTestId } = render(<AnalysisHistory history={mockHistory} onSelect={handleSelect} />);

    expect(getByTestId('history-item-1')).toBeTruthy();
    fireEvent.click(getByTestId('select-1'));
    expect(handleSelect).toHaveBeenCalledWith('1');
  });

  test('handles delete action when onDelete is provided', () => {
    const handleDelete = jest.fn();
    const { getByTestId } = render(<AnalysisHistory history={mockHistory} onSelect={() => {}} onDelete={handleDelete} />);

    fireEvent.click(getByTestId('delete-1'));
    expect(handleDelete).toHaveBeenCalledWith('1');
  });
});