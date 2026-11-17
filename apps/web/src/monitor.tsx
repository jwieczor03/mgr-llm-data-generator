import { useCallback, useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './monitor.css';

type Capacity = 'capable' | 'partial' | 'incapable';
type Check = { id: string; status: string; message: string };
type Service = { service: string; capacity: Capacity; checked_at: string; checks: Check[]; limitations: string[] };
type Report = { checked_at: string | null; freshness: string; in_progress: boolean; next_automatic_at: string; capacity: Capacity | null; services: Service[]; limitations: string[] };
const labels: Record<Capacity, string> = { capable: 'Zdolny do działania', partial: 'Częściowo zdolny do działania', incapable: 'Niezdolny do działania' };
const names: Record<string, string> = { 'application-api': 'API aplikacji', 'generation-service': 'Generator', 'validation-service': 'Walidator' };
const date = (value: string | null) => value ? new Intl.DateTimeFormat('pl-PL', { dateStyle: 'medium', timeStyle: 'medium', timeZoneName: undefined }).format(new Date(value)) + ' (' + Intl.DateTimeFormat().resolvedOptions().timeZone + ')' : 'Jeszcze nie sprawdzono';

export function Monitor() {
  const [report, setReport] = useState<Report | null>(null);
  const [offline, setOffline] = useState(false);
  const [starting, setStarting] = useState(false);
  const [announcement, setAnnouncement] = useState('');
  const [dark, setDark] = useState(() => window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false);
  const [now, setNow] = useState(Date.now());
  const wasInProgress = useRef(false);
  const refresh = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/report', { cache: 'no-store' });
      if (!response.ok) throw new Error();
      const data: Report = await response.json();
      if (wasInProgress.current && !data.in_progress) setAnnouncement('Kontrola zakończona. Wyniki zaktualizowano.');
      wasInProgress.current = data.in_progress;
      setReport(data);
      setOffline(false);
    } catch { setOffline(true); }
    setNow(Date.now());
  }, []);
  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => { const id = window.setInterval(() => { void refresh(); }, report?.in_progress || starting ? 2000 : 15000); return () => window.clearInterval(id); }, [refresh, report?.in_progress, starting]);
  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light'; }, [dark]);
  const run = async () => {
    setStarting(true); setAnnouncement('Kontrola w toku');
    try {
      const response = await fetch('/api/v1/check', { method: 'POST', headers: { 'X-Monitor-Request': '1' } });
      if (response.status !== 202 && response.status !== 409) throw new Error();
      await refresh();
    } catch { setAnnouncement('Nie udało się uruchomić kontroli. Spróbuj ponownie.'); }
    finally { setStarting(false); }
  };
  const stale = !!report?.checked_at && (report.freshness === 'stale' || now - Date.parse(report.checked_at) > 1830000);
  const busy = starting || !!report?.in_progress;
  return <main><header><div><h1>Stan serwisów</h1><p>Diagnostyka fundamentu aplikacji. Wyniki nie potwierdzają gotowości do generowania danych.</p></div><div className="actions"><button className="theme" onClick={() => setDark(!dark)}>{dark ? 'Włącz jasny motyw' : 'Włącz ciemny motyw'}</button><button className="primary" onClick={() => void run()} disabled={busy}>{busy ? 'Trwa sprawdzanie…' : 'Sprawdź teraz'}</button></div></header>
    <p className="announce" role="status" aria-live="polite">{busy ? 'Kontrola w toku' : announcement}</p>
    {offline && <p className="notice">Nie można odczytać wyników monitora. Sprawdź, czy usługa monitora działa. {report && 'Ostatni odebrany wynik — aktualny stan nieznany.'}</p>}
    <section className="summary"><h2>Stan fundamentu</h2><p className={'badge ' + (!stale && !offline && report?.capacity ? report.capacity : '')}>{stale || offline ? 'Ostatni znany wynik: ' : ''}{report?.capacity ? labels[report.capacity] : 'Jeszcze nie sprawdzono'}</p>{stale && <p className="notice">Wynik jest nieaktualny. Uruchom nową kontrolę. Wynik nieaktualny.</p>}<dl><div><dt>Ostatnia zakończona kontrola</dt><dd>{date(report?.checked_at ?? null)}</dd></div><div><dt>Następna kontrola automatyczna</dt><dd>{report ? date(report.next_automatic_at) : 'Nieznana'}</dd></div><div><dt>Aktualność wyniku</dt><dd>{offline ? 'Nieznana' : stale ? 'Wynik nieaktualny' : report?.freshness === 'fresh' ? 'Aktualny' : 'Jeszcze nie sprawdzono'}</dd></div></dl></section>
    {report?.limitations.some(item => item.startsWith('Harmonogram monitora')) && <p className="notice">Harmonogram monitora nie działa. Uruchom monitor ponownie.</p>}
    {Object.entries(names).map(([id, name]) => { const service = report?.services.find(item => item.service === id); const failed = service?.checks.filter(item => item.status !== 'ok') ?? []; return <section className="card" key={id}><h2>{name}</h2><p className={'badge ' + (!stale && !offline && service ? service.capacity : '')}>{service ? labels[service.capacity] : 'Jeszcze nie sprawdzono'}</p><p>Ostatnia kontrola: {date(service?.checked_at ?? null)}</p><h3>Przyczyny</h3>{failed.length ? <ul>{failed.map(item => <li key={item.id}>{item.message}</li>)}</ul> : <p>{service ? 'Nie wykryto problemów w sprawdzonym zakresie.' : 'Brak wyniku.'}</p>}<h3>Ograniczenia</h3><ul>{(service?.limitations ?? ['Brak wyniku diagnostyki.']).map(text => <li key={text}>{text}</li>)}</ul>{service && <details><summary>Szczegóły sprawdzeń</summary><ul>{service.checks.map(item => <li key={item.id}>{item.id}: {item.message}</li>)}</ul></details>}</section>; })}
    <p>Kontrole odbywają się przy uruchomieniu i co 30 minut. „Sprawdź teraz” nie zmienia harmonogramu. Diagnostyka nie uruchamia generowania, walidacji danych ani płatnych prób LLM.</p>
  </main>;
}
if (document.getElementById('root')) createRoot(document.getElementById('root')!).render(<Monitor />);
