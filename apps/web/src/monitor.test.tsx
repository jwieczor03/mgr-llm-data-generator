// @vitest-environment jsdom
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import { Monitor } from './monitor';

const snapshot = { scope: 'foundation', checked_at: new Date().toISOString(), freshness: 'fresh', in_progress: false, next_automatic_at: new Date().toISOString(), capacity: 'partial', services: [], limitations: [] };
afterEach(() => { vi.restoreAllMocks(); });

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
