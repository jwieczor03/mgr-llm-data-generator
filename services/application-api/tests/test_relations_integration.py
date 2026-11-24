import os
from datetime import timedelta
from uuid import uuid4

import pytest
from application_api.ddl_parser import DdlParser
from application_api.ddl_repository import PROFILE, now
from application_api.ddl_support import DdlSupport
from application_api.projects import ProjectError
from application_api.relation_worker import RelationWorker
from application_api.relations import decide, discover, readiness, relations, snapshot
from sqlalchemy import text
from test_ddl_parser import bundle_for

pytestmark = [pytest.mark.integration, pytest.mark.skipif(os.getenv('RUN_DATABASE_TESTS') != '1', reason='wymaga izolowanego Docker PostgreSQL')]


def setup_schema(db, sql=b'CREATE TABLE parent (id int PRIMARY KEY); CREATE TABLE child (id int PRIMARY KEY, parent_id int);'):
    db.start()
    bundle = bundle_for(sql)
    parsed = DdlParser(lambda _: sql).parse(bundle, PROFILE)
    analysis = DdlSupport().diagnose(parsed, PROFILE)
    project, attempt, interpretation = uuid4(), uuid4(), uuid4()
    with db.session() as s:
        s.execute(text("INSERT INTO app.projects (id,owner_subject,name,name_key,created_at) VALUES (:id,'o','p','p',now())"), {'id': project})
        s.execute(text("""INSERT INTO app.ddl_attempts (id,project_id,owner_subject,page_id,reservation,reservation_hash,status)
            VALUES (:id,:project,'o',:page,'[]',:hash,'SUCCEEDED')"""), {'id': attempt, 'project': project, 'page': uuid4(), 'hash': '0'*64})
        s.execute(text("""INSERT INTO app.schema_versions (id,project_id,attempt_id,revision_no,manifest_hash,analysis_profile,status)
            VALUES (:id,:project,:attempt,1,:hash,:profile,'SUCCEEDED')"""),
            {'id': bundle.schema_version_id, 'project': project, 'attempt': attempt, 'hash': bundle.manifest_hash, 'profile': PROFILE.model_dump_json()})
        s.execute(text("""INSERT INTO app.schema_interpretations (id,project_id,schema_version_id,revision_no,analysis_profile,analysis)
            VALUES (:id,:project,:version,1,:profile,CAST(:analysis AS jsonb))"""),
            {'id': interpretation, 'project': project, 'version': bundle.schema_version_id, 'profile': PROFILE.model_dump_json(), 'analysis': analysis.model_dump_json()})
        s.execute(text('UPDATE app.projects SET default_schema_version_id=:version WHERE id=:project'), {'project': project, 'version': bundle.schema_version_id})
    tables = {t.name: str(t.table_id) for t in analysis.tables}
    columns = {(tables[next(t.name for t in analysis.tables if t.table_id == c.table_id)], c.name): str(c.column_id) for c in analysis.columns}
    proposal = {'source_table_id': tables['child'], 'target_table_id': tables['parent'],
                'column_pairs': [{'source_column_id': columns[(tables['child'], 'parent_id')], 'target_column_id': columns[(tables['parent'], 'id')]}], 'explanation': 'Możliwa relacja'}
    return project, bundle.schema_version_id, analysis, proposal


def test_discovery_decision_and_snapshot(db):
    project, version, analysis, proposal = setup_schema(db)
    request_id = uuid4()
    discovery_id = discover(db, project, version, request_id)
    assert discover(db, project, version, request_id) == discovery_id
    worker = RelationWorker(db, None, None)
    job = worker.claim()
    worker.publish(job, analysis, [proposal, proposal])
    with db.session() as s:
        before = readiness(s, project, version)
        items = relations(s, project, version)
    assert before['blockers'][0]['code'] == 'RELATION_REVIEW_PENDING'
    assert len(items) == 1 and items[0]['status'] == 'PENDING'
    id = items[0]['id']
    old_snapshot = snapshot(db, project, version)
    first = decide(db, project, version, id, 'o', 1, 'APPROVE', False)
    assert decide(db, project, version, id, 'o', 1, 'APPROVE', False) == first
    with pytest.raises(ProjectError) as stale:
        decide(db, project, version, id, 'o', 1, 'APPROVE', True)
    assert stale.value.code == 'RELATION_PROPOSAL_STALE'
    assert first['readiness']['ready']
    assert old_snapshot['relations'] == []
    assert snapshot(db, project, version)['relations'][0]['reference_required'] is False


def test_expired_job_cannot_publish(db):
    project, version, analysis, proposal = setup_schema(db)
    discover(db, project, version, uuid4())
    worker = RelationWorker(db, None, None)
    job = worker.claim()
    with db.session() as s:
        s.execute(text("UPDATE app.relation_discoveries SET deadline=:deadline WHERE id=:id"), {'deadline': now()-timedelta(seconds=1), 'id': job['id']})
    assert worker.claim() is None
    worker.publish(job, analysis, [proposal])
    with db.session() as s:
        assert relations(s, project, version) == []
        assert s.execute(text('SELECT status FROM app.relation_discoveries WHERE id=:id'), {'id': job['id']}).scalar_one() == 'FAILED'


def test_competing_decisions_serialize(db):
    from concurrent.futures import ThreadPoolExecutor

    project, version, analysis, proposal = setup_schema(db)
    discover(db, project, version, uuid4())
    worker = RelationWorker(db, None, None)
    worker.publish(worker.claim(), analysis, [proposal])
    with db.session() as s:
        id = relations(s, project, version)[0]['id']

    def decide_one(required):
        try:
            return decide(db, project, version, id, 'o', 1, 'APPROVE', required)['reference_required']
        except ProjectError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(decide_one, [True, False]))
    assert results.count('RELATION_PROPOSAL_STALE') == 1
    with db.session() as s:
        assert s.execute(text('SELECT count(*) FROM app.relation_decisions')).scalar_one() == 1
        assert readiness(s, project, version)['requirements_revision'] == 2


def test_carry_forward_missing_column_remains_rejectable(db):
    from application_api.relations import carry_forward

    project, version, analysis, proposal = setup_schema(db)
    discover(db, project, version, uuid4())
    worker = RelationWorker(db, None, None)
    worker.publish(worker.claim(), analysis, [proposal])
    with db.session() as s:
        id = relations(s, project, version)[0]['id']
    decide(db, project, version, id, 'o', 1, 'APPROVE', False)
    sql = b'CREATE TABLE parent (id int PRIMARY KEY); CREATE TABLE child (id int PRIMARY KEY);'
    bundle = bundle_for(sql)
    new_analysis = DdlSupport().diagnose(DdlParser(lambda _: sql).parse(bundle, PROFILE), PROFILE)
    attempt, interpretation = uuid4(), uuid4()
    with db.session() as s:
        s.execute(text("""INSERT INTO app.ddl_attempts (id,project_id,owner_subject,page_id,reservation,reservation_hash,status)
            VALUES (:id,:project,'o',:page,'[]',:hash,'SUCCEEDED')"""), {'id': attempt, 'project': project, 'page': uuid4(), 'hash': '0'*64})
        s.execute(text("""INSERT INTO app.schema_versions (id,project_id,attempt_id,revision_no,manifest_hash,analysis_profile,status)
            VALUES (:id,:project,:attempt,2,:hash,:profile,'SUCCEEDED')"""),
            {'id': bundle.schema_version_id, 'project': project, 'attempt': attempt, 'hash': bundle.manifest_hash, 'profile': PROFILE.model_dump_json()})
        s.execute(text("""INSERT INTO app.schema_interpretations (id,project_id,schema_version_id,revision_no,analysis_profile,analysis)
            VALUES (:id,:project,:version,1,:profile,CAST(:analysis AS jsonb))"""),
            {'id': interpretation, 'project': project, 'version': bundle.schema_version_id, 'profile': PROFILE.model_dump_json(), 'analysis': new_analysis.model_dump_json()})
        carry_forward(s, project, version, bundle.schema_version_id, interpretation, new_analysis)
        items = relations(s, project, bundle.schema_version_id)
    assert len(items) == 1 and items[0]['source'] == 'CARRIED_FORWARD' and items[0]['invalid_reason']
    with pytest.raises(ProjectError) as invalid:
        decide(db, project, bundle.schema_version_id, items[0]['id'], 'o', 1, 'APPROVE', False)
    assert invalid.value.code == 'RELATION_DEFINITION_INVALID'
    result = decide(db, project, bundle.schema_version_id, items[0]['id'], 'o', 1, 'REJECT', None)
    assert result['readiness']['ready']


def test_pending_reason_tracks_approved_graph(db):
    project, version, analysis, proposal = setup_schema(db)
    tables = {t.name: str(t.table_id) for t in analysis.tables}
    columns = {(str(c.table_id), c.name): str(c.column_id) for c in analysis.columns}
    reverse = {'source_table_id': tables['parent'], 'target_table_id': tables['child'],
               'column_pairs': [{'source_column_id': columns[(tables['parent'], 'id')],
                                 'target_column_id': columns[(tables['child'], 'id')]}], 'explanation': 'reverse'}
    discover(db, project, version, uuid4())
    worker = RelationWorker(db, None, None)
    worker.publish(worker.claim(), analysis, [proposal, reverse])
    with db.session() as s:
        items = relations(s, project, version)
    assert all(item['invalid_reason'] is None for item in items)
    first = next(item for item in items if item['source_table_id'] == tables['child'])
    second = next(item for item in items if item['source_table_id'] == tables['parent'])
    decide(db, project, version, first['id'], 'o', 1, 'APPROVE', False)
    with db.session() as s:
        updated = next(item for item in relations(s, project, version) if item['id'] == second['id'])
    assert 'cykl' in updated['invalid_reason']
    with pytest.raises(ProjectError) as invalid:
        decide(db, project, version, second['id'], 'o', 1, 'APPROVE', False)
    assert invalid.value.code == 'RELATION_DEFINITION_INVALID'
    discover(db, project, version, uuid4())
    worker.publish(worker.claim(), analysis, [reverse])
    with db.session() as s:
        pending = [item for item in relations(s, project, version) if item['status'] == 'PENDING']
    assert len(pending) == 2 and all('cykl' in item['invalid_reason'] for item in pending)



def test_reordered_ddl_fk_is_not_discovered(db):
    sql = (b'CREATE TABLE parent (id int PRIMARY KEY, a int, b int, UNIQUE(a,b)); '
           b'CREATE TABLE child (id int PRIMARY KEY, parent_id int, x int, y int, '
           b'FOREIGN KEY(x,y) REFERENCES parent(a,b));')
    project, version, analysis, _ = setup_schema(db, sql)
    tables = {t.name: str(t.table_id) for t in analysis.tables}
    columns = {(str(c.table_id), c.name): str(c.column_id) for c in analysis.columns}
    child, parent = tables['child'], tables['parent']
    def pair(source, target):
        return {'source_column_id': columns[(child, source)], 'target_column_id': columns[(parent, target)]}
    common = {'source_table_id': child, 'target_table_id': parent, 'explanation': 'relacja'}
    duplicate = common | {'column_pairs': [pair('y', 'b'), pair('x', 'a')]}
    other = common | {'column_pairs': [pair('x', 'b'), pair('y', 'a')]}
    discover(db, project, version, uuid4())
    worker = RelationWorker(db, None, None)
    worker.publish(worker.claim(), analysis, [duplicate, other])
    with db.session() as s:
        items = relations(s, project, version)
    assert [item['source'] for item in items].count('DDL') == 1
    proposed = [item for item in items if item['source'] == 'MODEL_PROPOSAL']
    assert len(proposed) == 1 and proposed[0]['column_pairs'] == other['column_pairs']
