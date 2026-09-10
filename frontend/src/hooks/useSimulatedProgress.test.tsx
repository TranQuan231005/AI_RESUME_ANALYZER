import { act, renderHook } from '@testing-library/react';
import { useSimulatedProgress } from './useSimulatedProgress';

describe('estimated progress', () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  test('advances while pending, caps below completion, and stops on error', () => {
    const { result, rerender, unmount } = renderHook(
      ({ status }: { status: 'pending' | 'error' | 'success' }) => useSimulatedProgress(status),
      { initialProps: { status: 'pending' as 'pending' | 'error' | 'success' } },
    );
    expect(result.current.percent).toBe(0);
    act(() => jest.advanceTimersByTime(10000));
    expect(result.current.percent).toBe(65);
    act(() => jest.advanceTimersByTime(20000));
    expect(result.current.percent).toBe(85);
    act(() => jest.advanceTimersByTime(30000));
    expect(result.current.percent).toBe(95);
    expect(result.current.canMinimize).toBe(true);
    act(() => jest.advanceTimersByTime(120000));
    expect(result.current.percent).toBe(95);
    rerender({ status: 'error' });
    expect(jest.getTimerCount()).toBe(0);
    rerender({ status: 'pending' });
    expect(result.current.percent).toBe(0);
    rerender({ status: 'success' });
    expect(result.current.percent).toBe(100);
    unmount();
    expect(jest.getTimerCount()).toBe(0);
  });
});
