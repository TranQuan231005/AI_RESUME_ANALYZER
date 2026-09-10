import React from 'react';
import '@testing-library/jest-dom';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { MatchProgress } from './MatchProgress';

describe('match progress overlay', () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  test('locks scroll, blocks escape while pending, enables minimizing after 60s and restores focus', () => {
    const trigger = document.createElement('button');
    document.body.appendChild(trigger);
    trigger.focus();
    const callbacks = { onMinimize: jest.fn(), onExpand: jest.fn(), onClose: jest.fn(), onRetry: jest.fn() };
    const { rerender, unmount } = render(<MatchProgress status="pending" error={null} minimized={false} {...callbacks} />);
    const dialog = screen.getByRole('dialog');
    expect(dialog).toContainElement(document.activeElement as HTMLElement);
    expect(document.body.style.overflow).toBe('hidden');
    fireEvent(dialog, new Event('cancel', { cancelable: true }));
    expect(callbacks.onClose).not.toHaveBeenCalled();
    expect(screen.queryByRole('button', { name: 'Minimize' })).toBeNull();
    act(() => jest.advanceTimersByTime(60000));
    fireEvent.click(screen.getByRole('button', { name: 'Minimize' }));
    expect(callbacks.onMinimize).toHaveBeenCalledTimes(1);
    rerender(<MatchProgress status="pending" error={null} minimized {...callbacks} />);
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.body.style.overflow).toBe('');
    expect(screen.getByRole('progressbar')).toHaveAttribute('value', '95');
    fireEvent.click(screen.getByRole('button', { name: 'Show progress' }));
    expect(callbacks.onExpand).toHaveBeenCalledTimes(1);
    rerender(<MatchProgress status="error" error="Network error" minimized={false} {...callbacks} />);
    expect(screen.getByRole('alert')).toHaveTextContent('Network error');
    expect(jest.getTimerCount()).toBe(0);
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(callbacks.onRetry).toHaveBeenCalledTimes(1);
    unmount();
    expect(document.body.style.overflow).toBe('');
    trigger.remove();
  });

  test('restores the trigger focus when the overlay unmounts', () => {
    const button = document.createElement('button');
    document.body.appendChild(button);
    button.focus();
    const { unmount } = render(<MatchProgress status="pending" error={null} minimized={false}
      onMinimize={jest.fn()} onExpand={jest.fn()} onClose={jest.fn()} onRetry={jest.fn()} />);
    unmount();
    expect(document.activeElement).toBe(button);
    expect(jest.getTimerCount()).toBe(0);
    button.remove();
  });
});
