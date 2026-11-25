// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import { Projects } from './Projects';

const response = (body: unknown, status = 200) => ({ ok: status < 400, status, json: async () => body });
const projects = [{ id: 'a', name: 'Bank', description: null }, { id: 'b', name: 'Sklep', description: null }];
beforeEach(() => {
  HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
  HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
function mockFetch(reserve: () => Promise<unknown>) {
  return vi.fn((url: string, init?: RequestInit) => {
    if (url.endsWith('/projects')) return Promise.resolve(response({ items: projects }));
    if (url.endsWith('/schema-versions')) return Promise.resolve(response({ items: [] }));
    if (url.endsWith('/ddl-processing')) return Promise.resolve(response({ busy: false, attempt_id: null, status: null }));
    if (init?.method === 'PUT') return reserve();
    return Promise.resolve(response({ error: { code: 'DDL_ATTEMPT_NOT_FOUND', message: 'Brak próby', details: {} } }, 404));
  });
}
test('wybór innego projektu nie przenosi wybranych plików', async () => {
  vi.stubGlobal('fetch', mockFetch(() => new Promise(() => {})));
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  const select = screen.getByRole('combobox', { name: 'Zapisane projekty' });
  fireEvent.change(select, { target: { value: 'a' } });
  await waitFor(() => expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(false));
  fireEvent.change(screen.getByLabelText('Pliki SQL'), { target: { files: [new File(['x'], 'bank.sql')] } });
  expect(screen.getByText('bank.sql')).toBeTruthy();
  fireEvent.change(select, { target: { value: 'b' } });
  await waitFor(() => expect(screen.queryByText('bank.sql')).toBeNull());
  expect((screen.getByRole('button', { name: 'Wyślij paczkę' }) as HTMLButtonElement).disabled).toBe(true);
});
test('lokalna rezerwacja blokuje inne projekty mimo odpowiedzi wolnego slotu', async () => {
  vi.stubGlobal('fetch', mockFetch(() => new Promise(() => {})));
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  const select = screen.getByRole('combobox', { name: 'Zapisane projekty' });
  fireEvent.change(select, { target: { value: 'a' } });
  await waitFor(() => expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(false));
  fireEvent.change(screen.getByLabelText('Pliki SQL'), { target: { files: [new File(['x'], 'bank.sql')] } });
  fireEvent.click(screen.getByRole('button', { name: 'Wyślij paczkę' }));
  fireEvent.change(select, { target: { value: 'b' } });
  await waitFor(() => expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(true));
  fireEvent.change(select, { target: { value: 'a' } });
  await waitFor(() => expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(true));
});


test('błąd odczytu zatrzymuje automatyczne sprawdzanie próby', async () => {
  const fetchMock = vi.fn((url: string, init?: RequestInit) => {
    if (url.endsWith('/projects')) return Promise.resolve(response({ items: projects }));
    if (url.endsWith('/schema-versions')) return Promise.resolve(response({ items: [] }));
    if (url.endsWith('/ddl-processing')) return Promise.resolve(response({ busy: false, attempt_id: null, status: null }));
    if (init?.method === 'PUT') return Promise.resolve(response({}));
    if (url.endsWith('/files')) return Promise.reject(new Error('przerwane połączenie'));
    return Promise.resolve(response({ error: { code: 'database_unavailable', message: 'Błąd', details: {} } }, 503));
  });
  vi.stubGlobal('fetch', fetchMock);
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  fireEvent.change(screen.getByRole('combobox', { name: 'Zapisane projekty' }), { target: { value: 'a' } });
  await waitFor(() => expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(false));
  fireEvent.change(screen.getByLabelText('Pliki SQL'), { target: { files: [new File(['x'], 'bank.sql')] } });
  fireEvent.click(screen.getByRole('button', { name: 'Wyślij paczkę' }));
  await screen.findByRole('button', { name: 'Sprawdź ponownie' });
  const count = fetchMock.mock.calls.filter(([url, init]) => url.includes('/ddl-attempts/') && !init?.method).length;
  vi.useFakeTimers();
  await act(async () => { await vi.advanceTimersByTimeAsync(11000); });
  expect(fetchMock.mock.calls.filter(([url, init]) => url.includes('/ddl-attempts/') && !init?.method)).toHaveLength(count);
  vi.useRealTimers();
});
