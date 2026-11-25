import { useCallback, useEffect, useRef, useState } from 'react';
import './monitor.css';
import { Projects } from './Projects';

type Status = 'checking' | 'connected' | 'failed';
const TIMEOUT_MS = 5000;

export function App() {
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [status, setStatus] = useState<Status>('checking');
  const [dark, setDark] = useState(() => window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false);
  const active = useRef<AbortController | null>(null);
  const timer = useRef<number | null>(null);

  const check = useCallback(async () => {
    if (active.current) return;
    const controller = new AbortController();
    active.current = controller;
    setStatus('checking');
    timer.current = window.setTimeout(() => {
      if (active.current !== controller) return;
      active.current = null;
      controller.abort();
      setStatus('failed');
    }, TIMEOUT_MS);
    try {
      const response = await fetch('/health/live', { signal: controller.signal, cache: 'no-store' });
      if (response.status !== 200) throw new Error();
      const data: unknown = await response.json();
      if (!data || typeof data !== 'object' || !('status' in data) || data.status !== 'ok') throw new Error();
      if (active.current === controller) setStatus('connected');
    } catch {
      if (active.current === controller) setStatus('failed');
    } finally {
      if (active.current === controller) {
        active.current = null;
        if (timer.current !== null) window.clearTimeout(timer.current);
        timer.current = null;
      }
    }
  }, []);

  useEffect(() => {
    void check();
    return () => {
      active.current?.abort();
      active.current = null;
      if (timer.current !== null) window.clearTimeout(timer.current);
    };
  }, [check]);
  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light'; }, [dark]);

  const labels: Record<Status, string> = {
    checking: 'Sprawdzanie połączenia…',
    connected: 'Połączenie z API działa',
    failed: 'Nie udało się potwierdzić połączenia z API',
  };
  return <main><header><div><h1>Generator danych</h1><p>Szkielet aplikacji</p></div><div className="actions"><button onClick={() => setProjectsOpen(true)}>Projekty</button><button onClick={() => setDark(!dark)}>{dark ? 'Włącz jasny motyw' : 'Włącz ciemny motyw'}</button></div></header>
    <section><h2>Połączenie z API</h2><p role="status" className={status === 'connected' ? 'capable badge' : status === 'failed' ? 'notice' : ''}>{labels[status]}</p>
      <p>Połączenie potwierdza działanie procesu API. Gotowość konfiguracji, bazy i pozostałych usług sprawdzisz w osobnym panelu diagnostycznym. Generowanie danych nie jest jeszcze dostępne.</p>
      <button className="primary" disabled={status === 'checking'} onClick={() => void check()}>Sprawdź połączenie</button>
    </section>
    <Projects open={projectsOpen} onClose={() => setProjectsOpen(false)} />
  </main>;
}
