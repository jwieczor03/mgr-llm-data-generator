import { useCallback,useEffect,useRef,useState } from 'react';
import { api,ApiError,json,projectPath,versionPath,type Project,type Attempt,type Version,type Analysis,type Relation,type Readiness,type Diagnostic } from './project-api';
import './projects.css';

const active=['RESERVED','RECEIVING','STAGED','ANALYSIS_PENDING','ANALYZING','RETRY_WAIT','CANCELLING','CLEANUP_FAILED'];
const preAck=['RESERVED','RECEIVING','STAGED'];
const busyMessage='Trwa przesyłanie lub analiza DDL. Poczekaj na zakończenie';
type Transfer={ project: string; id: string; page: string; acknowledged: boolean; localAbandon: boolean; uncertain: boolean; commandPending: boolean };

const statusLabels: Record<string,string>={ RESERVED: 'Przygotowanie wysyłki',RECEIVING: 'Przesyłanie plików',STAGED: 'Pliki zapisane roboczo, potwierdzanie odbioru',ANALYSIS_PENDING: 'Pliki zapisane. Analiza oczekuje na rozpoczęcie',ANALYZING: 'Analiza trwa',RETRY_WAIT: 'Oczekiwanie na automatyczne ponowienie analizy',CANCELLING: 'Trwa zatrzymywanie i usuwanie plików',CLEANUP_FAILED: 'Ponawianie usuwania plików',SUCCEEDED: 'Analiza zakończona',REJECTED_INPUT: 'Paczka odrzucona podczas wstępnego sprawdzenia',REJECTED_DDL: 'Analiza wykryła nieobsługiwany schemat',FAILED_TECHNICAL: 'Analiza nie powiodła się. Wgraj ponownie całą paczkę.',CANCELLED: 'Analiza przerwana',EXPIRED: 'Transfer wygasł' };
function message(error: unknown) { return error instanceof ApiError? error.code==='DDL_PROCESSING_IN_PROGRESS'? busyMessage:error.message:'Nie udało się połączyć z serwerem.'; }
function Diagnostics({ items,files=[] }: { items: Diagnostic[]|null|undefined; files?: { id: string; name: string; position: number }[] }) {
  if(!items?.length) return null;
  return <div>
    <h4>Diagnostyka</h4>
    <ul>
      {items.map((d,i) => {
        const file=d.file??files.find(f => f.id===d.location?.file_id)?.name; const positions=d.positions?.map(p => files.find(f => f.position===p)?.name??`pozycja ${p+1}`).join(', '); return <li key={i}>
          {file? `${file}${d.location? `, wiersz ${d.location.line}`:''}: `:''}{d.message??d.code}{positions? ` (${positions})`:''}
        </li>;
      })}
    </ul>
  </div>;
}
export function Projects({ open,onClose }: { open: boolean; onClose: () => void }) {
  const dialog=useRef<HTMLDialogElement>(null),confirm=useRef<HTMLDialogElement>(null),searchRef=useRef<HTMLInputElement>(null);
  const transfer=useRef<Transfer|null>(null),page=useRef(crypto.randomUUID()),channel=useRef<BroadcastChannel|null>(null),selection=useRef(''),generation=useRef(0),receipt=useRef<Promise<void>|null>(null),lastRead404=useRef(false), currentVersion=useRef<string|undefined>(undefined), detailsGeneration=useRef(0), remotePending=useRef(false), remoteTimer=useRef<number | null>(null), slotWasBusy=useRef(false), viewRequests=useRef(new Set<AbortController>()), viewController=useRef(new AbortController()), versionsRequest=useRef<{project: string; generation: number; promise: Promise<void>} | null>(null), versionsRefresh=useRef<Promise<void> | null>(null), pollRunning=useRef(false), discoveryTimer=useRef<number | null>(null), cancelTarget=useRef<{project: string; attempt: string} | null>(null);
  const [projects,setProjects]=useState<Project[]>([]),[project,setProject]=useState<Project|null>(null),[creating,setCreating]=useState(false);
  const [name,setName]=useState(''),[description,setDescription]=useState(''),[fields,setFields]=useState<Record<string,string>>({}),[error,setError]=useState('');
  const [files,setFiles]=useState<File[]>([]),[attempt,setAttempt]=useState<Attempt|null>(null),[unknown,setUnknown]=useState(false),[busy,setBusy]=useState(true),[localBusy,setLocalBusy]=useState(false);
  const [versions,setVersions]=useState<Version[]>([]),[analysis,setAnalysis]=useState<Analysis|null>(null),[relations,setRelations]=useState<Relation[]>([]),[readiness,setReadiness]=useState<Readiness|null>(null);
  const [query,setQuery]=useState(''),[table,setTable]=useState<string|null>(null),[choices,setChoices]=useState<Record<string,string>>({}),[discovery,setDiscovery]=useState(''),[tab,setTab]=useState<'ddl'|'structure'|'relations'>('ddl');
  const clearView = () => { viewController.current.abort(); viewController.current = new AbortController(); viewRequests.current.forEach(c => c.abort()); viewRequests.current.clear(); if (discoveryTimer.current !== null) window.clearTimeout(discoveryTimer.current); discoveryTimer.current = null; };
  const viewSignal = () => viewController.current.signal;
  const closeConfirm = () => { cancelTarget.current = null; if (confirm.current?.open) confirm.current.close(); };
  const choose=(p: Project|null) => { closeConfirm(); clearView(); if(selection.current!==(p?.id??'')) { setFiles([]); setQuery(''); setTable(null); setVersions([]); setAnalysis(null); setRelations([]); setReadiness(null); currentVersion.current = undefined; versionsRefresh.current = null; } generation.current++; selection.current=p?.id??''; setProject(p); };
  const broadcast=(kind: 'start' | 'refresh' = 'refresh') => channel.current?.postMessage(kind);
  const refreshProjects=useCallback(async () => { try { setProjects((await api<{ items: Project[] }>('/projects')).items); } catch(e) { setError(message(e)); } },[]);
  useEffect(() => { if(open) { dialog.current?.showModal(); void refreshProjects(); } else if(dialog.current?.open) dialog.current.close(); },[open,refreshProjects]);
  const refreshSlot = useCallback(async (id: string) => {
    const revision = generation.current;
    const signal = viewSignal();
    try {
      const result = await api<{ busy: boolean; attempt_id: string | null; status: string | null }>(`${projectPath(id)}/ddl-processing`, { signal });
      if (selection.current !== id || generation.current !== revision) return;
      const wasBusy = slotWasBusy.current;
      slotWasBusy.current = result.busy || remotePending.current;
      setBusy(slotWasBusy.current);
      if (wasBusy && !slotWasBusy.current) void refreshVersions(id);
      if (result.attempt_id && result.status && !preAck.includes(result.status) && !transfer.current) {
        setAttempt(previous => previous?.attempt_id === result.attempt_id ? previous : {
          attempt_id: result.attempt_id!, status: result.status!, schema_version_id: null,
        });
      }
    } catch (e) {
      if (!signal.aborted && selection.current === id && generation.current === revision) {
        setBusy(true); setUnknown(true); setError(message(e));
      }
    }
  }, []);
  async function acceptStaged(p: string, id: string, current: Attempt): Promise<Attempt> {
    if (current.status !== 'STAGED' || !current.receipt_nonce || transfer.current?.id !== id || transfer.current.localAbandon) return current;
    if (!receipt.current) {
      receipt.current = api(`${projectPath(p)}/ddl-attempts/${id}/receipt`, json('POST', {
        page_id: page.current, receipt_nonce: current.receipt_nonce,
      })).then(() => { if (transfer.current?.id === id) transfer.current.acknowledged = true; })
        .finally(() => { receipt.current = null; });
    }
    await receipt.current;
    return { ...current, status: 'ANALYSIS_PENDING', receipt_nonce: undefined };
  }
  async function readAttempt(p: string,id: string, owned = transfer.current?.id === id) {
    const revision=generation.current;
    lastRead404.current=false;
    const signal = owned ? undefined : viewSignal();
    try {
      let current=await api<Attempt>(`${projectPath(p)}/ddl-attempts/${id}`,{ headers: { 'X-DDL-Page-ID': page.current }, signal });
      if (signal?.aborted) return null;
      current = await acceptStaged(p, id, current);
      if(transfer.current?.id===id) {
        if(!preAck.includes(current.status)) transfer.current.acknowledged=true;
        transfer.current.uncertain=transfer.current.localAbandon&&preAck.includes(current.status);
        if (selection.current !== p && !transfer.current.uncertain) setUnknown(false);
      }
      if(selection.current===p&&generation.current===revision) { setAttempt(current); const uncertain=!!transfer.current?.localAbandon&&preAck.includes(current.status); setUnknown(uncertain); if(!uncertain) setError(''); }
      if(!active.includes(current.status)) { if (cancelTarget.current?.project === p && cancelTarget.current.attempt === id) closeConfirm(); slotWasBusy.current = false; if(transfer.current?.id===id) { transfer.current=null; setLocalBusy(false); if (selection.current && selection.current !== p) void refreshSlot(selection.current); } broadcast(); if(selection.current===p&&generation.current===revision) void refreshVersions(p); }
      return current;
    } catch(e) { if (signal?.aborted) return null; lastRead404.current=e instanceof ApiError&&e.status===404; if(transfer.current?.id===id) { transfer.current.uncertain=true; setUnknown(true); } if(selection.current===p&&generation.current===revision) { setUnknown(true); setBusy(true); setError(message(e)); } return null; }
  }
  function loadVersions(p: string): Promise<void> {
    const revision = generation.current;
    if (versionsRequest.current?.project === p && versionsRequest.current.generation === revision) return versionsRequest.current.promise;
    const signal = viewSignal();
    const promise = (async () => {
      try {
        const items = (await api<{ items: Version[] }>(`${projectPath(p)}/schema-versions`, { signal })).items;
        if (signal.aborted || selection.current !== p || generation.current !== revision) return;
        const next = items.find(v => v.status === 'SUCCEEDED')?.id;
        setVersions(items);
        if (next && next === currentVersion.current) void loadDetails(p, next);
      } catch (e) {
        if (!signal.aborted && selection.current === p && generation.current === revision) setError(message(e));
      }
    })().finally(() => { if (versionsRequest.current?.promise === promise) versionsRequest.current = null; });
    versionsRequest.current = { project: p, generation: revision, promise };
    return promise;
  }
  function refreshVersions(p: string) {
    if (versionsRefresh.current) return versionsRefresh.current;
    const revision = generation.current;
    const pending = versionsRequest.current?.project === p && versionsRequest.current.generation === revision
      ? versionsRequest.current.promise : null;
    const promise = (async () => {
      if (pending) await pending;
      if (selection.current === p && generation.current === revision) await loadVersions(p);
    })().finally(() => { if (versionsRefresh.current === promise) versionsRefresh.current = null; });
    versionsRefresh.current = promise;
    return promise;
  }
  useEffect(() => {
    if(!project) return;
    const id=project.id; selection.current=id; const own=transfer.current?.project===id? transfer.current:null; setAttempt(own? { attempt_id: own.id,status: 'RESERVED',schema_version_id: null }:null); setVersions([]); setAnalysis(null); setRelations([]); setReadiness(null); setBusy(true); setUnknown(!!transfer.current?.uncertain); setError('');
    void loadVersions(id); void refreshSlot(id);
    return () => { selection.current=''; clearView(); closeConfirm(); };
  },[project?.id]);
  useEffect(() => {
    const refresh = () => {
      remotePending.current = false;
      if (remoteTimer.current !== null) window.clearTimeout(remoteTimer.current);
      remoteTimer.current = null;
      if (selection.current) void refreshSlot(selection.current);
    };
    window.addEventListener('focus', refresh);
    if (typeof BroadcastChannel !== 'undefined') {
      channel.current = new BroadcastChannel('ddl-processing');
      channel.current.onmessage = event => {
        if (event.data === 'start') {
          remotePending.current = true; slotWasBusy.current = true; setBusy(true);
          if (remoteTimer.current !== null) window.clearTimeout(remoteTimer.current);
          remoteTimer.current = window.setTimeout(refresh, 3000);
        } else if (event.data === 'refresh') refresh();
      };
    }
    return () => { window.removeEventListener('focus', refresh); channel.current?.close(); channel.current = null; if (remoteTimer.current !== null) window.clearTimeout(remoteTimer.current); clearView(); };
  }, [refreshSlot]);
  useEffect(() => {
    if (!project || unknown || (!busy && !localBusy && !active.includes(attempt?.status ?? ''))) return;
    let timer = 0;
    let stopped = false;
    let running = false;
    const poll = async () => {
      if (stopped) return;
      if (pollRunning.current) { timer = window.setTimeout(poll, document.visibilityState === 'visible' ? 2000 : 10000); return; }
      running = true; pollRunning.current = true;
      const t = transfer.current;
      if (t && !t.uncertain && !t.commandPending) {
        await readAttempt(t.project, t.id);
      } else if (!t && attempt && active.includes(attempt.status)) {
        await readAttempt(project.id, attempt.attempt_id);
      } else {
        await refreshSlot(project.id);
      }
      running = false; pollRunning.current = false;
      if (!stopped) timer = window.setTimeout(poll, document.visibilityState === 'visible' ? 2000 : 10000);
    };
    timer = window.setTimeout(poll, document.visibilityState === 'visible' ? 2000 : 10000);
    const visibility = () => { window.clearTimeout(timer); if (!running) timer = window.setTimeout(poll, document.visibilityState === 'visible' ? 2000 : 10000); };
    document.addEventListener('visibilitychange', visibility);
    return () => { stopped = true; window.clearTimeout(timer); document.removeEventListener('visibilitychange', visibility); };
  }, [project?.id, attempt?.status, attempt?.attempt_id, unknown, busy, localBusy, refreshSlot]);
  useEffect(() => {
    const timer = window.setInterval(() => {
      const t = transfer.current;
      if (t && !t.acknowledged && !t.localAbandon) {
        void api(`${projectPath(t.project)}/ddl-attempts/${t.id}/lease`, json('POST', { page_id: t.page })).catch(() => {});
      }
    }, 15000);
    const before = (e: BeforeUnloadEvent) => { if (transfer.current && !transfer.current.acknowledged) { e.preventDefault(); e.returnValue = ''; } };
    const hide = () => {
      const t = transfer.current;
      if (t && !t.acknowledged) void fetch(`/api/v1${projectPath(t.project)}/ddl-attempts/${t.id}/abandon`, { ...json('POST', { page_id: t.page }), keepalive: true });
    };
    window.addEventListener('beforeunload', before);
    window.addEventListener('pagehide', hide);
    return () => { window.clearInterval(timer); window.removeEventListener('beforeunload', before); window.removeEventListener('pagehide', hide); };
  }, []);
  useEffect(() => { if (cancelTarget.current && (!project || cancelTarget.current.project !== project.id || cancelTarget.current.attempt !== attempt?.attempt_id || !['ANALYSIS_PENDING','ANALYZING','RETRY_WAIT'].includes(attempt.status))) closeConfirm(); }, [project?.id, attempt?.attempt_id, attempt?.status]);
  const version=versions.find(v => v.status==='SUCCEEDED');
  const versionId=version?.id;
  currentVersion.current = versionId;
  const loadDetails=useCallback(async (p: string,v: string,signal?: AbortSignal) => {
    const revision=generation.current, request = ++detailsGeneration.current;
    signal ??= viewSignal();
    try { const [a,r,ready]=await Promise.all([api<Analysis>(`${versionPath(p,v)}/analysis`,{ signal }),api<{ items: Relation[] }>(`${versionPath(p,v)}/relations`,{ signal }),api<Readiness>(`${versionPath(p,v)}/readiness`,{ signal })]); if(selection.current===p&&generation.current===revision&&currentVersion.current===v&&detailsGeneration.current===request&&!signal?.aborted) { setAnalysis(a); setRelations(r.items); setReadiness(ready); } } catch(e) { if(!signal?.aborted&&selection.current===p&&generation.current===revision&&currentVersion.current===v&&detailsGeneration.current===request) setError(message(e)); }
  },[]);
  useEffect(() => { if(!project||!versionId) return; clearView(); const controller=new AbortController(); viewRequests.current.add(controller); setAnalysis(null); setRelations([]); setReadiness(null); void loadDetails(project.id,versionId,controller.signal); return () => { controller.abort(); clearView(); }; },[project?.id,versionId,loadDetails]);
  async function create(e: React.FormEvent) { e.preventDefault(); setError(''); setFields({}); try { const p=await api<Project>('/projects',json('POST',{ name,description })); setProjects(old => [p,...old]); choose(p); setCreating(false); setName(''); setDescription(''); } catch(e) { setError(message(e)); if(e instanceof ApiError) setFields(Object.fromEntries((e.details?.fields??[]).map(f => [f.field,f.message]))); } }
  async function upload() {
    if(!project||!files.length) return;
    const revision=generation.current,p=project.id,id=crypto.randomUUID(),metadata=files.map(f => ({ name: f.name,size_bytes: f.size })),body={ page_id: page.current,files: metadata };
    transfer.current={ project: p,id,page: page.current,acknowledged: false,localAbandon: false,uncertain: false,commandPending: true }; setLocalBusy(true); setAttempt({ attempt_id: id,status: 'RESERVED',schema_version_id: null }); setBusy(true); setUnknown(false); setError(''); broadcast('start');
    let reserved=false;
    try { await api(`${projectPath(p)}/ddl-attempts/${id}`,json('PUT',body)); reserved=true; }
    catch(e) {
      if(e instanceof ApiError&&e.status>=400&&e.status<500) { transfer.current=null; setLocalBusy(false); if (selection.current === p && generation.current === revision) setError(message(e)); broadcast(); if (selection.current === p && generation.current === revision) void refreshSlot(p); return; }
      const found=await readAttempt(p,id);
      if(found?.status==='RESERVED') reserved=true;
      else if(!found&&lastRead404.current&&e instanceof Error) { try { await api(`${projectPath(p)}/ddl-attempts/${id}`,json('PUT',body)); reserved=true; } catch { /* outcome remains uncertain */ } }
    }
    if (reserved) broadcast();
    if(!reserved) { if(transfer.current) { transfer.current.localAbandon=true; transfer.current.uncertain=true; } setUnknown(true); setBusy(true); return; }
    try { const data=new FormData(); files.forEach(f => data.append('files',f)); const staged = await api<Attempt>(`${projectPath(p)}/ddl-attempts/${id}/files`,{ method: 'POST',headers: { 'X-DDL-Page-ID': page.current },body: data }); if (transfer.current?.id === id) transfer.current.commandPending = false; const accepted = await acceptStaged(p,id,staged); if (selection.current === p && generation.current === revision) { setAttempt(accepted); setUnknown(false); }  }
    catch(e) { if (transfer.current?.id === id) transfer.current.commandPending = false; if(e instanceof ApiError&&e.details?.diagnostics) { if(selection.current===p && generation.current===revision) setAttempt({ attempt_id: id,status: 'REJECTED_INPUT',schema_version_id: null,diagnostics: e.details.diagnostics }); } await readAttempt(p,id); }
  }
  async function decide(r: Relation,decision: 'APPROVE'|'REJECT') { if(!project||!versionId) return; const p=project.id,v=versionId, revision=generation.current; try { await api(`${versionPath(p,v)}/relation-proposals/${r.id}/decision`,json('POST',{ expected_revision: r.revision,decision,...(decision==='APPROVE'? { reference_required: choices[r.id]==='required' }:{}) })); } catch(e) { if (selection.current === p && generation.current === revision && currentVersion.current === v) setError(message(e)); } if (selection.current === p && generation.current === revision && currentVersion.current === v) await loadDetails(p,v); }
  async function discover() { if(!project||!versionId) return; const p=project.id,v=versionId, revision=generation.current; try { const { discovery_id }=await api<{ discovery_id: string }>(`${versionPath(p,v)}/relation-discoveries`,json('POST',{ request_id: crypto.randomUUID() })); if (selection.current !== p || generation.current !== revision || currentVersion.current !== v) return; setDiscovery('Poszukiwanie propozycji trwa'); const poll=async () => { const signal = viewSignal(); try { const d=await api<{ status: string; error_code: string|null }>(`${versionPath(p,v)}/relation-discoveries/${discovery_id}`, { signal }); if (signal.aborted) return; if(selection.current!==p || generation.current!==revision || currentVersion.current!==v) return; if(['PENDING','RUNNING'].includes(d.status)) discoveryTimer.current = window.setTimeout(() => void poll(),2000); else { setDiscovery(d.status==='SUCCEEDED'? 'Poszukiwanie zakończone':`Poszukiwanie nie powiodło się: ${d.error_code??''}`); void loadDetails(p,v); } } catch(e) { if (!signal.aborted && selection.current === p && generation.current === revision && currentVersion.current === v) setDiscovery(message(e)); } }; void poll(); } catch(e) { if (selection.current === p && generation.current === revision && currentVersion.current === v) setError(message(e)); } }
  const matched=analysis?.tables.filter(t => `${t.schema_name}.${t.name}`.toLocaleLowerCase().includes(query.toLocaleLowerCase()))??[];
  const tableName=(id: string,fallback?: string[]) => { const t=analysis?.tables.find(x => x.table_id===id); return t? `${t.schema_name}.${t.name}`:fallback?.join('.')??id; };
  const columnName=(id: string,fallback?: string[]) => analysis?.columns.find(c => c.column_id===id)?.name??fallback?.join('.')??id;
  return <dialog ref={dialog} className="projects-dialog" aria-labelledby="projects-title" onCancel={e => { e.preventDefault(); onClose(); }}>
    <div className="dialog-heading">
      <div>
        <p className="eyebrow">Przygotowanie danych</p>
        <h2 id="projects-title">Projekty</h2>
      </div>
      <button onClick={onClose}>Zamknij</button>
    </div>
    <div className="projects-layout">
      <nav aria-label="Zapisane projekty">
        <label htmlFor="project-select">Zapisane projekty</label>
        <select id="project-select" value={project?.id??""} onChange={e => { const selected=projects.find(p => p.id===e.target.value)??null; choose(selected); setCreating(false); }}>
          <option value="">Wybierz projekt</option>
          {projects.map(p => <option key={p.id} value={p.id}>
            {p.name}
          </option>)}
        </select>
        {projects.length===0&&<p>Nie ma jeszcze projektów.</p>}<button onClick={() => { setCreating(true); choose(null); }}>Nowy projekt</button>
      </nav>
      <div className="project-content">
        {error&&<p className="notice" role="alert">
          {error}
        </p>}{creating? <form onSubmit={create} noValidate>
          <h3>Nowy projekt</h3>
          <label>Nazwa<input value={name} onChange={e => setName(e.target.value)} aria-invalid={!!fields.name} aria-describedby={fields.name? 'name-error':undefined} />
          </label>
          {fields.name&&<p id="name-error" className="notice">
            {fields.name}
          </p>}<label>Opis (opcjonalnie)<textarea className="resize-none" value={description} onChange={e => setDescription(e.target.value)} aria-invalid={!!fields.description} />
          </label>
          {fields.description&&<p className="notice">
            {fields.description}
          </p>}<button className="primary" type="submit">Utwórz projekt</button>
        </form>:!project? <p>Wybierz projekt lub utwórz nowy.</p>:<>
          <h3>
            {project.name}
          </h3>
          {project.description&&<p>
            {project.description}
          </p>}<div className="project-tabs" aria-label="Sekcje projektu">
            {([["ddl","DDL"],["structure","Struktura"],["relations","Relacje"]] as const).map(([key,label]) => <button key={key} aria-pressed={tab===key} onClick={() => setTab(key)}>
              {label}
            </button>)}
          </div>
          <section hidden={tab!=="ddl"}>
            <h3>DDL</h3>
            <p>Prześlij pełną paczkę plików SQL w kolejności wykonania.</p>
            <label>Pliki SQL<input type="file" accept=".sql" multiple onChange={e => setFiles(Array.from(e.target.files??[]))} disabled={busy||localBusy||unknown} />
            </label>
            <ol>
              {files.map((f,i) => <li key={`${f.name}-${i}`}>
                <span>
                  {f.name}
                </span> <button disabled={i===0||busy||localBusy} aria-label={`Przenieś ${f.name} w górę`} onClick={() => setFiles(old => { const n=[...old];[n[i-1],n[i]]=[n[i],n[i-1]]; return n; })}>↑</button> <button disabled={i===files.length-1||busy||localBusy} aria-label={`Przenieś ${f.name} w dół`} onClick={() => setFiles(old => { const n=[...old];[n[i+1],n[i]]=[n[i],n[i+1]]; return n; })}>↓</button>
              </li>)}
            </ol>
            <button className="primary" disabled={!files.length||busy||localBusy||unknown} onClick={() => void upload()}>Wyślij paczkę</button>
            {(busy||localBusy)&&<p>
              {busyMessage}
            </p>}{attempt&&<>
              <p role="status">
                {statusLabels[attempt.status]??attempt.status}
              </p>
              <Diagnostics items={attempt.diagnostics} files={files.map((f,i) => ({ id: '',name: f.name,position: i }))} />
              {['ANALYSIS_PENDING','ANALYZING','RETRY_WAIT'].includes(attempt.status)&&<button onClick={() => { cancelTarget.current = { project: project.id, attempt: attempt.attempt_id }; confirm.current?.showModal(); }}>Przerwij analizę</button>}
            </>}{unknown&&<>
              <p>Nie ustalono wyniku próby. Wysyłanie pozostaje zablokowane.</p>
              <button onClick={() => { const t=transfer.current; if(t) void readAttempt(t.project,t.id); else if(attempt) void readAttempt(project.id,attempt.attempt_id); else { setUnknown(false); void refreshSlot(project.id); } }}>Sprawdź ponownie</button>
            </>}{transfer.current&&!transfer.current.acknowledged&&<p>Odświeżenie lub zamknięcie strony może anulować transfer.</p>}{version&&<div>
              <h4>Domyślna wersja {version.revision_no}
              </h4>
              <p>Analiza zakończona. Zapisane pliki w kolejności:</p>
              <ol>
                {version.files.map(f => <li key={f.id}>
                  {f.name}
                </li>)}
              </ol>
            </div>}{versions.filter(v => v.status!=='SUCCEEDED').map(v => <div key={v.id}>
              <p>Wersja {v.revision_no}: {statusLabels[v.status]??v.status}
              </p>
              <Diagnostics items={v.diagnostics} files={v.files} />
            </div>)}
          </section>
          <section>
            <h3>Gotowość schematu</h3>
            {readiness? <>
              <p>
                {readiness.ready? 'Schemat gotowy według dostępnych kontroli.':'Schemat wymaga przygotowania.'}
              </p>
              <ul>
                {readiness.blockers.map((b,i) => <li key={i}>
                  {b.message}
                </li>)}
              </ul>
              <p>Kontrola reguł będzie dostępna w kolejnym etapie.</p>
            </>:<p>Brak przeanalizowanego schematu.</p>}
          </section>
          <section hidden={tab!=="structure"}>
            <h3>Struktura</h3>
            {analysis? <>
              <label>Wyszukaj tabelę<input ref={searchRef} value={query} onChange={e => setQuery(e.target.value)} />
              </label>
              {query&&<button onClick={() => { setQuery(''); searchRef.current?.focus(); }}>Wyczyść wyszukiwanie</button>}<p>
                {matched.length} wyników</p>
              <ul>
                {matched.map(t =>
                  <li key={t.table_id}>
                    <button onClick={() => setTable(t.table_id)}>
                      {t.schema_name}.{t.name}
                    </button>
                  </li>)}
              </ul>
              {table&&analysis.tables.some(t => t.table_id===table)&&<div>
                <h4 className="identifier">
                  {tableName(table)}
                </h4>
                <h5>Kolumny</h5>
                <ul>
                  {analysis.columns.filter(c => c.table_id===table).map(c =>
                    <li key={c.column_id}>
                      <span className="identifier">
                        {c.name}
                      </span> — {c.type.name}, {c.nullable? 'dopuszcza NULL':'NOT NULL'}
                    </li>)}
                </ul>
                <h5>Ograniczenia</h5>
                <ul>
                  {analysis.constraints.filter(c => c.table_id===table).map(c =>
                    <li key={c.constraint_id}>
                      {c.name??'Bez nazwy'} — {c.kind}
                    </li>)}
                </ul>
              </div>}
            </>:<p>Struktura pojawi się po pomyślnej analizie.</p>}
          </section>
          <section hidden={tab!=="relations"}>
            <h3>Relacje</h3>
            <button disabled={!versionId} onClick={() => void discover()}>Szukaj dodatkowych relacji</button>
            <p role="status">
              {discovery}
            </p>
            {['DDL','additional'].map(group => <div key={group}>
              <h4>
                {group==='DDL'? 'Relacje z DDL':'Relacje dodatkowe'}
              </h4>
              {relations.filter(r => group==='DDL'? r.source==='DDL':r.source!=='DDL').map(r =>
                <article key={r.id}>
                  <p className="identifier">
                    {tableName(r.source_table_id,r.original_names?.source_table)} → {tableName(r.target_table_id,r.original_names?.target_table)}
                  </p>
                  <p>
                    {r.source==='CARRIED_FORWARD'&&r.status==='PENDING'? 'Wymaga ponownego przeglądu':({ PENDING: 'Oczekuje na decyzję',APPROVED: 'Zatwierdzona',REJECTED: 'Odrzucona' }[r.status]??r.status)}
                  </p>
                  {r.explanation&&<p>
                    {r.explanation}
                  </p>}<ul>
                    {r.column_pairs.map((pair,index) => <li className="identifier" key={index}>
                      {columnName(pair.source_column_id,r.original_names?.source_columns?.[index])} → {columnName(pair.target_column_id,r.original_names?.target_columns?.[index])}
                    </li>)}
                  </ul>
                  {r.invalid_reason&&<p>
                    {r.invalid_reason}
                  </p>}{r.status==='PENDING'&&<>
                    <fieldset>
                      <legend>Obowiązkowość odwołania</legend>
                      <label>
                        <input type="radio" name={`required-${r.id}`} checked={choices[r.id]==='required'} onChange={() => setChoices({ ...choices,[r.id]: 'required' })} /> Odwołanie obowiązkowe</label>
                      <p>Wszystkie wartości muszą być podane; błędny klucz jest odrzucany.</p>
                      <label>
                        <input type="radio" name={`required-${r.id}`} checked={choices[r.id]==='optional'} onChange={() => setChoices({ ...choices,[r.id]: 'optional' })} /> Odwołanie opcjonalne</label>
                      <p>Wszystkie wartości mogą być NULL, jeśli pozwala DDL. Częściowy NULL i błędny klucz są odrzucane.</p>
                    </fieldset>
                    <button disabled={!choices[r.id]||!!r.invalid_reason} onClick={() => void decide(r,'APPROVE')}>Zatwierdź</button> <button onClick={() => void decide(r,'REJECT')}>Odrzuć</button>
                  </>}
                </article>)}
            </div>)}
          </section>
        </>}
      </div>
    </div>
    <dialog ref={confirm} aria-labelledby="cancel-title" onClose={() => { cancelTarget.current = null; }}>
      <h2 id="cancel-title">Przerwać analizę?</h2>
      <p>Pliki tej wersji i częściowy wynik analizy zostaną usunięte.</p>
      <div className="actions">
        <button autoFocus onClick={closeConfirm}>Kontynuuj analizę</button>
        <button onClick={() => { const target = cancelTarget.current; closeConfirm(); if (target && project?.id === target.project && attempt?.attempt_id === target.attempt && ['ANALYSIS_PENDING','ANALYZING','RETRY_WAIT'].includes(attempt.status)) void api(`${projectPath(target.project)}/ddl-attempts/${target.attempt}/cancel`,json('POST',{ page_id: page.current })).then(() => readAttempt(target.project,target.attempt)).catch(e => { if (selection.current === target.project) setError(message(e)); }); }}>Przerwij analizę</button>
      </div>
    </dialog>
  </dialog>;
}
