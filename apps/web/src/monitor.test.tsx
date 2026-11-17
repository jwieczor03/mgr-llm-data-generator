// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import { Monitor } from './monitor';

const snapshot = { scope: 'foundation', checked_at: new Date().toISOString(), freshness: 'fresh', in_progress: false, next_automatic_at: new Date().toISOString(), capacity: 'partial', services: [], limitations: [] };
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

test('odczytuje raport i uruchamia nową kontrolę', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true, status: 200, json: async () => snapshot } as Response);
  render(<Monitor />);
  await screen.findByText('Częściowo zdolny do działania');
  fireEvent.click(screen.getByRole('button', { name: 'Sprawdź teraz' }));
  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/v1/check', expect.objectContaining({ method: 'POST', headers: { 'X-Monitor-Request': '1' } })));
});

test('pokazuje błąd odczytu i nie przypisuje mu sukcesu', async () => {
  vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('offline'));
  render(<Monitor />);
  await screen.findByText(/Nie można odczytać wyników monitora/);
  expect(screen.getAllByText('Jeszcze nie sprawdzono').length).toBeGreaterThan(0);
});

test('szybko zakończona kontrola ogłasza ukończenie', async () => {
  let manual = false;
  vi.spyOn(globalThis, 'fetch').mockImplementation(async url => {
    if (url === '/api/v1/check') { manual = true; return { ok: true, status: 202, json: async () => ({ run_id: 'run-1', status: 'running' }) } as Response; }
    return { ok: true, status: 200, json: async () => ({ ...snapshot, checked_at: manual ? new Date(Date.parse(snapshot.checked_at) + 1000).toISOString() : snapshot.checked_at }) } as Response;
  });
  render(<Monitor />);
  await screen.findByText('Częściowo zdolny do działania');
  fireEvent.click(screen.getByRole('button', { name: 'Sprawdź teraz' }));
  await waitFor(() => expect(screen.getByRole('status').textContent).toBe('Kontrola zakończona. Wyniki zaktualizowano.'));
});

test('utrata łączności nie przedstawia starej kontroli jako trwającej', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ ...snapshot, in_progress: true }) } as Response).mockRejectedValue(new Error('offline'));
  render(<Monitor />);
  await screen.findByText('Częściowo zdolny do działania');
  await screen.findByText(/Nie można odczytać wyników monitora/, {}, { timeout: 3500 });
  expect(screen.getByRole('status').textContent).toBe('Nie można potwierdzić stanu kontroli.');
});
