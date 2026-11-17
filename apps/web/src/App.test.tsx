// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import { App } from './App';

afterEach(() => { cleanup(); vi.useRealTimers(); vi.unstubAllGlobals(); });
const ok = () => Promise.resolve({ status: 200, json: async () => ({ status: 'ok' }) });

test('sprawdza połączenie i pokazuje ograniczenia wyniku', async () => {
  const fetchMock = vi.fn(ok); vi.stubGlobal('fetch', fetchMock);
  render(<App />);
  expect(screen.getByRole('status').textContent).toBe('Sprawdzanie połączenia…');
  expect((screen.getByRole('button', { name: 'Sprawdź połączenie' }) as HTMLButtonElement).disabled).toBe(true);
  await screen.findByText('Połączenie z API działa');
  expect(fetchMock).toHaveBeenCalledWith('/health/live', expect.objectContaining({ cache: 'no-store', signal: expect.any(AbortSignal) }));
  expect(screen.getByText(/Gotowość konfiguracji, bazy/)).toBeTruthy();
});

test.each([
  ['HTTP', () => Promise.resolve({ status: 503 })],
  ['sieci', () => Promise.reject(new Error('secret'))],
  ['JSON', () => Promise.resolve({ status: 200, json: async () => { throw new Error(); } })],
  ['treści', () => Promise.resolve({ status: 200, json: async () => ({ status: 'bad' }) })],
])('obsługuje błąd %s i ponowienie', async (_name, fail) => {
  const fetchMock = vi.fn().mockImplementationOnce(fail).mockImplementationOnce(ok); vi.stubGlobal('fetch', fetchMock);
  render(<App />);
  await screen.findByText('Nie udało się potwierdzić połączenia z API');
  fireEvent.click(screen.getByRole('button', { name: 'Sprawdź połączenie' }));
  await screen.findByText('Połączenie z API działa');
  expect(fetchMock).toHaveBeenCalledTimes(2);
});

test('limit czasu przerywa żądanie i ignoruje spóźnioną odpowiedź', async () => {
  vi.useFakeTimers();
  let resolve!: (value: unknown) => void;
  const fetchMock = vi.fn().mockImplementationOnce(() => new Promise(r => { resolve = r; })).mockImplementationOnce(ok);
  vi.stubGlobal('fetch', fetchMock); const view = render(<App />);
  const signal = fetchMock.mock.calls[0][1].signal as AbortSignal;
  await act(async () => { vi.advanceTimersByTime(5000); });
  expect(signal.aborted).toBe(true);
  expect(screen.getByRole('status').textContent).toBe('Nie udało się potwierdzić połączenia z API');
  fireEvent.click(screen.getByRole('button', { name: 'Sprawdź połączenie' }));
  await act(async () => { resolve({ status: 200, json: async () => ({ status: 'bad' }) }); });
  expect(screen.getByRole('status').textContent).toBe('Połączenie z API działa');
  view.unmount();
});

test('odmontowanie przerywa kontrolę i nie nakłada kolejnej', async () => {
  const fetchMock = vi.fn((_url: string, _options: RequestInit) => new Promise(() => {})); vi.stubGlobal('fetch', fetchMock);
  const view = render(<App />); fireEvent.click(screen.getByRole('button', { name: 'Sprawdź połączenie' }));
  expect(fetchMock).toHaveBeenCalledTimes(1);
  const signal = fetchMock.mock.calls[0][1].signal as AbortSignal;
  view.unmount(); expect(signal.aborted).toBe(true);
});
