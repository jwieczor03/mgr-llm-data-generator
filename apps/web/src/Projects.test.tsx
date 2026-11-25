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

test('potwierdza STAGED z odpowiedzi uploadu bez wcześniejszego GET', async () => {
  const fetchMock = vi.fn((url: string, init?: RequestInit) => {
    if (url.endsWith('/projects')) return Promise.resolve(response({ items: projects }));
    if (url.endsWith('/schema-versions')) return Promise.resolve(response({ items: [] }));
    if (url.endsWith('/ddl-processing')) return Promise.resolve(response({ busy: false, attempt_id: null, status: null }));
    if (init?.method === 'PUT') return Promise.resolve(response({}));
    if (url.endsWith('/files')) return Promise.resolve(response({ attempt_id: 'id', status: 'STAGED', receipt_nonce: 'nonce', schema_version_id: null }, 201));
    if (url.endsWith('/receipt')) return Promise.resolve(response({ schema_version_id: 'v' }, 202));
    return Promise.reject(new Error('GET jest niedostępny'));
  });
  vi.stubGlobal('fetch', fetchMock);
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  fireEvent.change(screen.getByRole('combobox', { name: 'Zapisane projekty' }), { target: { value: 'a' } });
  await waitFor(() => expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(false));
  fireEvent.change(screen.getByLabelText('Pliki SQL'), { target: { files: [new File(['x'], 'bank.sql')] } });
  fireEvent.click(screen.getByRole('button', { name: 'Wyślij paczkę' }));
  await waitFor(() => expect(fetchMock.mock.calls.some(([url]) => url.endsWith('/receipt'))).toBe(true));
  expect(fetchMock.mock.calls.filter(([url, init]) => url.includes('/ddl-attempts/') && !init?.method)).toHaveLength(0);
});

test('zmiana projektu zamyka potwierdzenie przerwania poprzedniej próby', async () => {
  const fetchMock = vi.fn((url: string, init?: RequestInit) => {
    void init;
    if (url.endsWith('/projects')) return Promise.resolve(response({ items: projects }));
    if (url.endsWith('/schema-versions')) return Promise.resolve(response({ items: [] }));
    if (url.endsWith('/ddl-processing')) return Promise.resolve(response({ busy: true, attempt_id: 'attempt-a', status: 'ANALYZING' }));
    return Promise.resolve(response({ attempt_id: 'attempt-a', status: 'ANALYZING', schema_version_id: 'v' }));
  });
  vi.stubGlobal('fetch', fetchMock);
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  const select = screen.getByRole('combobox', { name: 'Zapisane projekty' });
  fireEvent.change(select, { target: { value: 'a' } });
  const cancel = await screen.findByRole('button', { name: 'Przerwij analizę' });
  fireEvent.click(cancel);
  expect(screen.getByRole('dialog', { name: 'Przerwać analizę?' }).hasAttribute('open')).toBe(true);
  fireEvent.change(select, { target: { value: 'b' } });
  expect(screen.queryByRole('dialog', { name: 'Przerwać analizę?' })).toBeNull();
  expect(fetchMock.mock.calls.some(([url, init]) => url.endsWith('/cancel') && init?.method === 'POST')).toBe(false);
});

test('odświeża wersję po krótkim przetwarzaniu w innej karcie', async () => {
  let broadcast!: { onmessage: ((event: {data: string}) => void) | null };
  class Channel {
    onmessage: ((event: {data: string}) => void) | null = null;
    constructor() { broadcast = this; }
    postMessage() {}
    close() {}
  }
  vi.stubGlobal('BroadcastChannel', Channel);
  let completed = false;
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    if (url.endsWith('/projects')) return Promise.resolve(response({ items: projects }));
    if (url.endsWith('/ddl-processing')) return Promise.resolve(response({ busy: false, attempt_id: null, status: null }));
    if (url.endsWith('/schema-versions')) return Promise.resolve(response({ items: completed ? [{ id: 'v1', status: 'SUCCEEDED', revision_no: 1, files: [{ id: 'f', name: 'nowy.sql', position: 0 }], diagnostics: [] }] : [] }));
    if (url.endsWith('/analysis')) return Promise.resolve(response({ tables: [], columns: [], constraints: [], diagnostics: [] }));
    if (url.endsWith('/relations')) return Promise.resolve(response({ items: [] }));
    if (url.endsWith('/readiness')) return Promise.resolve(response({ ready: true, blockers: [] }));
    return Promise.reject(new Error('nieoczekiwany adres'));
  }));
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  fireEvent.change(screen.getByRole('combobox', { name: 'Zapisane projekty' }), { target: { value: 'a' } });
  await waitFor(() => expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(false));
  act(() => broadcast.onmessage?.({ data: 'start' }));
  completed = true;
  act(() => broadcast.onmessage?.({ data: 'refresh' }));
  expect(await screen.findByText('nowy.sql')).toBeTruthy();
  expect(await screen.findByText('Schemat gotowy według dostępnych kontroli.')).toBeTruthy();
});

test('zmiana projektu przerywa odczyt wersji poprzedniego widoku', async () => {
  let oldSignal: AbortSignal | undefined;
  vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
    if (url.endsWith('/projects')) return Promise.resolve(response({ items: projects }));
    if (url.endsWith('/ddl-processing')) return Promise.resolve(response({ busy: false, attempt_id: null, status: null }));
    if (url.includes('/projects/a/schema-versions')) {
      oldSignal = init?.signal as AbortSignal;
      return new Promise(() => {});
    }
    return Promise.resolve(response({ items: [] }));
  }));
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  const select = screen.getByRole('combobox', { name: 'Zapisane projekty' });
  fireEvent.change(select, { target: { value: 'a' } });
  await waitFor(() => expect(oldSignal).toBeDefined());
  fireEvent.change(select, { target: { value: 'b' } });
  expect(oldSignal?.aborted).toBe(true);
});

test('nowe zakończenie podczas odczytu wersji zleca kolejny świeży odczyt', async () => {
  let channel!: { onmessage: ((event: {data: string}) => void) | null };
  class Channel { onmessage: ((event: {data: string}) => void) | null = null; constructor() { channel = this; } postMessage() {} close() {} }
  vi.stubGlobal('BroadcastChannel', Channel);
  let versionsReads = 0;
  let finishOld!: (value: ReturnType<typeof response>) => void;
  const fetchMock = vi.fn((url: string) => {
    if (url.endsWith('/projects')) return Promise.resolve(response({ items: projects }));
    if (url.endsWith('/ddl-processing')) return Promise.resolve(response({ busy: false, attempt_id: null, status: null }));
    if (url.endsWith('/schema-versions')) {
      versionsReads++;
      if (versionsReads === 2) return new Promise<ReturnType<typeof response>>(resolve => { finishOld = resolve; });
      return Promise.resolve(response({ items: versionsReads >= 3 ? [{ id: 'v2', status: 'SUCCEEDED', revision_no: 2, files: [{ id: 'f', name: 'najnowszy.sql', position: 0 }], diagnostics: [] }] : [] }));
    }
    if (url.endsWith('/analysis')) return Promise.resolve(response({ tables: [], columns: [], constraints: [], diagnostics: [] }));
    if (url.endsWith('/relations')) return Promise.resolve(response({ items: [] }));
    if (url.endsWith('/readiness')) return Promise.resolve(response({ ready: true, blockers: [] }));
    throw new Error(url);
  });
  vi.stubGlobal('fetch', fetchMock);
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  fireEvent.change(screen.getByRole('combobox', { name: 'Zapisane projekty' }), { target: { value: 'a' } });
  await waitFor(() => expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(false));
  act(() => { channel.onmessage?.({ data: 'start' }); channel.onmessage?.({ data: 'refresh' }); });
  await waitFor(() => expect(versionsReads).toBe(2));
  act(() => { channel.onmessage?.({ data: 'start' }); channel.onmessage?.({ data: 'refresh' }); });
  await act(async () => { await Promise.resolve(); await Promise.resolve(); });
  await act(async () => { finishOld(response({ items: [] })); });
  expect(await screen.findByText('najnowszy.sql')).toBeTruthy();
  expect(versionsReads).toBe(3);
});

test.each(['sukces', 'błąd'])('starszy %s slotu nie nadpisuje nowszej blokady', async (outcome) => {
  let oldResolve!: (value: ReturnType<typeof response>) => void;
  let oldReject!: (reason: Error) => void;
  let slotCalls = 0;
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    if (url.endsWith('/projects')) return Promise.resolve(response({ items: projects }));
    if (url.endsWith('/schema-versions')) return Promise.resolve(response({ items: [] }));
    if (url.endsWith('/ddl-processing')) {
      slotCalls++;
      if (slotCalls === 1) return new Promise<ReturnType<typeof response>>((resolve, reject) => { oldResolve = resolve; oldReject = reject; });
      return Promise.resolve(response({ busy: true, attempt_id: null, status: null }));
    }
    throw new Error(url);
  }));
  render(<Projects open onClose={() => {}} />);
  await screen.findByRole('option', { name: 'Bank' });
  fireEvent.change(screen.getByRole('combobox', { name: 'Zapisane projekty' }), { target: { value: 'a' } });
  await waitFor(() => expect(slotCalls).toBe(1));
  fireEvent.focus(window);
  await waitFor(() => expect(slotCalls).toBe(2));
  await act(async () => { if (outcome === 'sukces') oldResolve(response({ busy: false, attempt_id: null, status: null })); else oldReject(new Error('stary błąd')); });
  expect((screen.getByLabelText('Pliki SQL') as HTMLInputElement).disabled).toBe(true);
  expect(screen.queryByRole('alert')).toBeNull();
});
