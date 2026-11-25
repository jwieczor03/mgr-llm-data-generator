export type Project = { id: string; name: string; description: string | null; created_at: string };
export type Diagnostic = { code: string; message?: string; file?: string; position?: number; positions?: number[]; location?: { file_id: string; line: number } | null };
export type Attempt = { attempt_id: string; status: string; schema_version_id: string | null; receipt_nonce?: string; diagnostics?: Diagnostic[] | null };
export type Version = { id: string; status: string; revision_no: number; diagnostics: Diagnostic[] | null; files: { id: string; name: string; position: number }[] };
export type Analysis = { tables: { table_id: string; schema_name: string; name: string; original_name: string }[]; columns: { column_id: string; table_id: string; name: string; type: { name: string }; nullable: boolean }[]; constraints: { constraint_id: string; table_id: string; kind: string; name: string | null }[]; diagnostics: Diagnostic[] };
export type Relation = { id: string; revision: number; source: string; status: string; source_table_id: string; target_table_id: string; column_pairs: { source_column_id: string; target_column_id: string }[]; reference_required: boolean | null; invalid_reason?: string | null; original_names?: { source_table?: string[]; target_table?: string[]; source_columns?: string[][]; target_columns?: string[][] }; explanation?: string };
export type Readiness = { ready: boolean; blockers: { code: string; source: string; object_id: string | null; message: string }[] };
export class ApiError extends Error { constructor(public status: number, public code: string, message: string, public details: { fields?: { field: string; message: string }[]; diagnostics?: Diagnostic[] } = {}) { super(message); } }
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api/v1${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.error?.code ?? '', body.error?.message ?? 'Nie udało się połączyć z serwerem.', body.error?.details);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
export const json = (method: string, body: unknown): RequestInit => ({ method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
export const projectPath = (project: string) => `/projects/${project}`;
export const versionPath = (project: string, version: string) => `${projectPath(project)}/schema-versions/${version}`;
