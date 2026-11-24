"""Durable, fenced discovery consumer; failed calls are never retried."""
import json
import threading
from datetime import timedelta
from uuid import uuid4

import httpx
from sqlalchemy import text

from application_api.artifact_store import ArtifactRef
from application_api.ddl_repository import now, sha256
from application_api.relation_validation import definition_error
from application_api.relations import lock_project, row
from application_api.schema_contracts import (
    DdlBundle,
    ManifestFile,
    SchemaAnalysis,
    manifest_digest,
)


class RelationWorker:
    def __init__(self, database, artifacts, url):
        self.database, self.artifacts, self.url = database, artifacts, url
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True, name='relation-worker')
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=3)

    def claim(self):
        with self.database.session() as session:
            session.execute(text("UPDATE app.relation_discoveries SET status='FAILED', error_code='RELATION_DISCOVERY_EXPIRED' WHERE status='RUNNING' AND deadline<=now()"))
            job = row(session, "SELECT * FROM app.relation_discoveries WHERE status='PENDING' ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1")
            if job is None:
                return None
            deadline = now() + timedelta(seconds=120)
            session.execute(text("UPDATE app.relation_discoveries SET status='RUNNING', deadline=:deadline WHERE id=:id"),
                            {'deadline': deadline, 'id': job['id']})
            return dict(job) | {'deadline': deadline}

    def run(self):
        while not self.stop_event.is_set():
            try:
                job = self.claim()
                if job:
                    self.process(job)
                else:
                    self.stop_event.wait(0.5)
            except Exception:
                self.stop_event.wait(1)

    def process(self, job):
        try:
            with self.database.session() as session:
                state = row(session, '''SELECT v.manifest_hash, v.attempt_id, i.analysis FROM app.schema_versions v
                    JOIN app.schema_interpretations i ON i.id=:interpretation AND i.schema_version_id=v.id WHERE v.id=:version''',
                    interpretation=job['interpretation_id'], version=job['schema_version_id'])
                files = list(session.execute(text('''SELECT id,position,name,size_bytes,sha256,artifact_id FROM app.ddl_attempt_files
                    WHERE attempt_id=:attempt ORDER BY position'''), {'attempt': state['attempt_id']}).mappings())
                manifest = [ManifestFile(file_id=f['id'], position=f['position'], name=f['name'],
                                         size_bytes=f['size_bytes'], sha256=f['sha256'], artifact_id=f['artifact_id']) for f in files]
                bundle = DdlBundle(schema_version_id=job['schema_version_id'], manifest_hash=state['manifest_hash'], files=manifest)
                if manifest_digest(bundle.files) != bundle.manifest_hash or [f.position for f in manifest] != list(range(len(manifest))):
                    raise ValueError('manifest mismatch')
                analysis = SchemaAnalysis.model_validate(state['analysis'])
            contents = []
            for f in files:
                content = self.artifacts.get(ArtifactRef('project', str(f['artifact_id'])))
                if len(content) != f['size_bytes'] or sha256(content) != f['sha256']:
                    raise ValueError('artifact mismatch')
                contents.append(content.decode('utf-8-sig'))
            tables = [{'id': str(t.table_id), 'name': f'{t.schema_name}.{t.name}',
                       'columns': [{'id': str(c.column_id), 'name': c.name} for c in analysis.columns if c.table_id == t.table_id]}
                      for t in analysis.tables]
            payload = {'context': {'project_id': str(job['project_id']), 'preparation_operation_id': str(job['id']),
                       'schema_version_id': str(job['schema_version_id']), 'ddl_hash': state['manifest_hash'],
                       'ddl': '\n'.join(contents), 'tables': tables}}
            with httpx.Client(timeout=httpx.Timeout(115, connect=3), trust_env=False, follow_redirects=False) as client:
                response = client.post(self.url.rstrip('/') + '/internal/v1/relation-proposals', json=payload)
                response.raise_for_status()
                result = response.json()
            proposals = result['relations']
            if not isinstance(proposals, list):
                raise ValueError('bad response')
            self.publish(job, analysis, proposals)
        except Exception:
            with self.database.session() as session:
                session.execute(text("UPDATE app.relation_discoveries SET status='FAILED',error_code='RELATION_DISCOVERY_FAILED' WHERE id=:id AND status='RUNNING' AND deadline=:deadline"),
                                {'id': job['id'], 'deadline': job['deadline']})

    def publish(self, job, analysis, proposals):
        known_tables = {str(t.table_id) for t in analysis.tables}
        known_columns = {str(c.column_id): str(c.table_id) for c in analysis.columns}
        unique = {}
        ddl = {(str(r.source_table_id), str(r.target_table_id), tuple((str(a), str(b)) for a,b in r.column_pairs)) for r in analysis.relations}
        for p in proposals:
            if not isinstance(p, dict) or set(p) != {'source_table_id', 'target_table_id', 'column_pairs', 'explanation'}:
                raise ValueError('bad response')
            source, target, pairs = p['source_table_id'], p['target_table_id'], p['column_pairs']
            if source not in known_tables or target not in known_tables or not isinstance(pairs, list) or not pairs or not isinstance(p['explanation'], str) or not p['explanation']:
                raise ValueError('bad response')
            if any(not isinstance(pair, dict) or set(pair) != {'source_column_id', 'target_column_id'} for pair in pairs):
                raise ValueError('bad response')
            links = tuple((pair['source_column_id'], pair['target_column_id']) for pair in pairs)
            if (len({s for s,t in links}) != len(links) or len({t for s,t in links}) != len(links)
                or any(known_columns.get(s) != source or known_columns.get(t) != target for s,t in links)):
                raise ValueError('bad response')
            key = (source, target, links)
            if key not in ddl:
                unique.setdefault(key, p)
        with self.database.session() as session:
            lock_project(session, job['project_id'])
            current = row(session, 'SELECT * FROM app.relation_discoveries WHERE id=:id FOR UPDATE', id=job['id'])
            if current['status'] != 'RUNNING' or current['deadline'] != job['deadline'] or current['deadline'] <= now():
                return
            for p in unique.values():
                reason = definition_error(analysis, p, [])
                session.execute(text('''INSERT INTO app.relation_proposals (id,project_id,schema_version_id,interpretation_id,discovery_id,source,definition,invalid_reason)
                    VALUES (:id,:project,:version,:interpretation,:discovery,'MODEL_PROPOSAL',CAST(:definition AS jsonb),:reason)'''),
                    {'id': uuid4(), 'project': job['project_id'], 'version': job['schema_version_id'],
                     'interpretation': job['interpretation_id'], 'discovery': job['id'],
                     'definition': json.dumps(p, ensure_ascii=False), 'reason': reason})
            if unique:
                session.execute(text('UPDATE app.projects SET requirements_revision=requirements_revision+1 WHERE id=:id'), {'id': job['project_id']})
            session.execute(text("UPDATE app.relation_discoveries SET status='SUCCEEDED' WHERE id=:id"), {'id': job['id']})
