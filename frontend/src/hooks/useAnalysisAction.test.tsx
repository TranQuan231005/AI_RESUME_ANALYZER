import { act, renderHook } from '@testing-library/react';
import { useAnalysisAction } from './useAnalysisAction';

describe('analysis request lifecycle', () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  test('blocks duplicate submissions and waits only 400ms after real match success', async () => {
    let resolve!: (value: string) => void;
    const request = jest.fn(() => new Promise<string>((done) => { resolve = done; }));
    const success = jest.fn();
    const unauthorized = jest.fn();
    const { result } = renderHook(() => useAnalysisAction('token'));
    act(() => {
      void result.current.run('match', request, success, unauthorized);
      void result.current.run('match', request, success, unauthorized);
    });
    expect(request).toHaveBeenCalledTimes(1);
    expect(result.current.matchStatus).toBe('pending');
    await act(async () => resolve('report'));
    expect(result.current.matchStatus).toBe('success');
    expect(success).not.toHaveBeenCalled();
    act(() => jest.advanceTimersByTime(400));
    expect(success).toHaveBeenCalledWith('report');
    expect(result.current.busy).toBe(false);
  });

  test('ignores an old session response and clears completion timers on unmount', async () => {
    let resolve!: (value: string) => void;
    const request = () => new Promise<string>((done) => { resolve = done; });
    const success = jest.fn();
    const { result, rerender, unmount } = renderHook(({ token }) => useAnalysisAction(token), { initialProps: { token: 'old' } });
    act(() => { void result.current.run('match', request, success, jest.fn()); });
    rerender({ token: 'new' });
    await act(async () => resolve('old report'));
    expect(success).not.toHaveBeenCalled();
    expect(result.current.matchStatus).toBe('idle');
    await act(async () => { await result.current.run('match', async () => 'new report', success, jest.fn()); });
    unmount();
    act(() => jest.advanceTimersByTime(1000));
    expect(success).not.toHaveBeenCalled();
    expect(jest.getTimerCount()).toBe(0);
  });

  test('reports errors, allows manual retry, and preserves the 401 callback', async () => {
    const success = jest.fn();
    const unauthorized = jest.fn();
    const { result } = renderHook(() => useAnalysisAction('token'));
    await act(async () => { await result.current.run('match', async () => { throw new Error('Offline'); }, success, unauthorized); });
    expect(result.current.matchStatus).toBe('error');
    expect(result.current.matchError).toBe('Offline');
    expect(result.current.busy).toBe(false);
    await act(async () => { await result.current.run('match', async () => { throw Object.assign(new Error('Expired'), { status: 401 }); }, success, unauthorized); });
    expect(unauthorized).toHaveBeenCalledTimes(1);
    expect(result.current.matchStatus).toBe('idle');
    expect(success).not.toHaveBeenCalled();
  });

  test('does not navigate when a pending request finishes after unmount', async () => {
    let resolve!: (value: string) => void;
    const success = jest.fn();
    const { result, unmount } = renderHook(() => useAnalysisAction('token'));
    act(() => { void result.current.run('resume', () => new Promise<string>((done) => { resolve = done; }), success, jest.fn()); });
    unmount();
    await act(async () => resolve('late report'));
    expect(success).not.toHaveBeenCalled();
    expect(jest.getTimerCount()).toBe(0);
  });
});
