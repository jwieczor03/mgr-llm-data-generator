"""Transactional review of relations pinned to a schema interpretation."""
import json
from uuid import uuid4

from sqlalchemy import text

from application_api.projects import ProjectError
from application_api.relation_validation import definition_error
from application_api.schema_contracts import SchemaAnalysis


def row(session, sql, **params):
    return session.execute(text(sql), params).mappings().first()


def lock_project(session, project):
    return row(session, 'SELECT * FROM app.projects WHERE id=:project FOR UPDATE', project=project)


def version(session, project, schema_version):
    result = row(session, '''SELECT v.*, i.id AS interpretation_id, i.analysis FROM app.schema_versions v
        LEFT JOIN app.schema_interpretations i ON i.schema_version_id=v.id
        WHERE v.project_id=:project AND v.id=:version ORDER BY i.revision_no DESC LIMIT 1''',
        project=project, version=schema_version)
    if result is None:
        raise ProjectError(404, 'SCHEMA_VERSION_NOT_FOUND', 'Nie znaleziono wersji.')
    return result


def approved(session, schema_version):
    return list(session.execute(text('''SELECT p.*, d.id AS decision_id, d.reference_required FROM app.relation_proposals p
        JOIN app.relation_decisions d ON d.proposal_id=p.id AND d.decision='APPROVE'
        WHERE p.schema_version_id=:version'''), {'version': schema_version}).mappings())


def readiness(session, project, schema_version):
    if schema_version is None:
        revision = session.execute(text('SELECT requirements_revision FROM app.projects WHERE id=:id'), {'id': project}).scalar_one()
        return {'schema_version_id': None, 'requirements_revision': revision, 'ready': False,
                'blockers': [{'code': 'SCHEMA_MISSING', 'source': 'S2', 'object_id': None, 'message': 'Brak schematu.'}]}
    state = version(session, project, schema_version)
    revision = session.execute(text('SELECT requirements_revision FROM app.projects WHERE id=:id'), {'id': project}).scalar_one()
    blockers = []
    if state['status'] in ('ANALYSIS_PENDING', 'ANALYZING', 'RETRY_WAIT'):
        blockers.append({'code': 'SCHEMA_ANALYSIS_PENDING', 'source': 'S2', 'object_id': str(schema_version), 'message': 'Analiza schematu trwa.'})
    elif state['status'] != 'SUCCEEDED' or state['analysis'] is None:
        blockers.append({'code': 'SCHEMA_UNSUPPORTED', 'source': 'S2', 'object_id': str(schema_version), 'message': 'Schemat nie jest obsługiwany.'})
    pending = session.execute(text('''SELECT p.id FROM app.relation_proposals p LEFT JOIN app.relation_decisions d ON d.proposal_id=p.id
        WHERE p.schema_version_id=:version AND d.id IS NULL ORDER BY p.id'''), {'version': schema_version}).scalars()
    blockers.extend({'code': 'RELATION_REVIEW_PENDING', 'source': 'S2', 'object_id': str(id), 'message': 'Relacja wymaga decyzji.'} for id in pending)
    return {'schema_version_id': str(schema_version), 'requirements_revision': revision, 'ready': not blockers, 'blockers': blockers}


def relations(session, project, schema_version):
    state = version(session, project, schema_version)
    items = []
    if state['analysis']:
        analysis = SchemaAnalysis.model_validate(state['analysis'])
        for r in analysis.relations:
            items.append({'id': str(r.constraint_id), 'schema_version_id': str(schema_version), 'revision': 1,
                          'source': 'DDL', 'status': 'APPROVED', 'source_table_id': str(r.source_table_id),
                          'target_table_id': str(r.target_table_id), 'column_pairs': [
                              {'source_column_id': str(a), 'target_column_id': str(b)} for a, b in r.column_pairs],
                          'reference_required': None, 'ddl': r.model_dump(mode='json')})
    effective = [p['definition'] for p in approved(session, schema_version)] if state['analysis'] else []
    rows = session.execute(text('''SELECT p.*, d.id AS decision_id, d.decision, d.reference_required FROM app.relation_proposals p
        LEFT JOIN app.relation_decisions d ON d.proposal_id=p.id WHERE p.schema_version_id=:version ORDER BY p.id'''),
        {'version': schema_version}).mappings()
    for p in rows:
        reason = p['invalid_reason']
        if p['decision'] is None and state['analysis']:
            reason = reason or definition_error(analysis, p['definition'], effective)
        items.append(p['definition'] | {'id': str(p['id']), 'schema_version_id': str(schema_version), 'revision': p['revision'],
                     'source': p['source'], 'status': {'APPROVE': 'APPROVED', 'REJECT': 'REJECTED'}.get(p['decision'], 'PENDING'),
                     'reference_required': p['reference_required'], 'invalid_reason': reason,
                     'decision_id': str(p['decision_id']) if p['decision_id'] else None})
    return items


def decide(database, project, schema_version, proposal_id, owner, expected_revision, decision, required):
    with database.session() as session:
        lock_project(session, project)
        state = version(session, project, schema_version)
        p = row(session, '''SELECT p.*, d.id AS decision_id, d.proposal_revision, d.decision, d.reference_required
            FROM app.relation_proposals p LEFT JOIN app.relation_decisions d ON d.proposal_id=p.id
            WHERE p.project_id=:project AND p.schema_version_id=:version AND p.id=:id''',
            project=project, version=schema_version, id=proposal_id)
        if p is None:
            raise ProjectError(404, 'RELATION_PROPOSAL_NOT_FOUND', 'Nie znaleziono propozycji.')
        if p['decision_id']:
            if p['proposal_revision'] != expected_revision or p['decision'] != decision or p['reference_required'] != required:
                raise ProjectError(409, 'RELATION_PROPOSAL_STALE', 'Propozycja została już rozpatrzona.')
            decision_id = p['decision_id']
        else:
            if p['revision'] != expected_revision or p['interpretation_id'] != state['interpretation_id']:
                raise ProjectError(409, 'RELATION_PROPOSAL_STALE', 'Propozycja jest nieaktualna.')
            if decision == 'APPROVE':
                analysis = SchemaAnalysis.model_validate(state['analysis'])
                error = p['invalid_reason'] or definition_error(analysis, p['definition'], [x['definition'] for x in approved(session, schema_version)], required)
                if error:
                    raise ProjectError(422, 'RELATION_DEFINITION_INVALID', error)
            decision_id = uuid4()
            session.execute(text('''INSERT INTO app.relation_decisions
                (id, proposal_id, proposal_revision, decision, reference_required, owner_subject)
                VALUES (:id,:proposal,:revision,:decision,:required,:owner)'''),
                {'id': decision_id, 'proposal': proposal_id, 'revision': expected_revision, 'decision': decision,
                 'required': required, 'owner': owner})
            session.execute(text('UPDATE app.projects SET requirements_revision=requirements_revision+1 WHERE id=:id'), {'id': project})
        return {'decision_id': str(decision_id), 'proposal_id': str(proposal_id), 'decision': decision,
                'reference_required': required, 'readiness': readiness(session, project, schema_version)}


def carry_forward(session, project, old_version, new_version, interpretation, analysis):
    if old_version is None:
        return
    previous = version(session, project, old_version)
    old = SchemaAnalysis.model_validate(previous['analysis'])
    def names(schema):
        tables = {str(t.table_id): (t.schema_name, t.name) for t in schema.tables}
        columns = {str(c.column_id): (*tables[str(c.table_id)], c.name) for c in schema.columns}
        return tables, columns
    old_tables, old_columns = names(old)
    new_tables, new_columns = names(analysis)
    table_ids = {v: k for k, v in new_tables.items()}
    column_ids = {v: k for k, v in new_columns.items()}
    for p in approved(session, old_version):
        old_definition = p['definition']
        definition = dict(old_definition)
        source_name = old_tables.get(definition['source_table_id'])
        target_name = old_tables.get(definition['target_table_id'])
        source_names = [old_columns.get(pair['source_column_id']) for pair in definition['column_pairs']]
        target_names = [old_columns.get(pair['target_column_id']) for pair in definition['column_pairs']]
        definition['original_names'] = {'source_table': source_name, 'target_table': target_name,
                                        'source_columns': source_names, 'target_columns': target_names}
        definition['source_table_id'] = table_ids.get(source_name, definition['source_table_id'])
        definition['target_table_id'] = table_ids.get(target_name, definition['target_table_id'])
        definition['column_pairs'] = [
            {'source_column_id': column_ids.get(s, pair['source_column_id']),
             'target_column_id': column_ids.get(t, pair['target_column_id'])}
            for s, t, pair in zip(source_names, target_names, definition['column_pairs'])]
        reason = definition_error(analysis, definition, [])
        session.execute(text('''INSERT INTO app.relation_proposals
            (id,project_id,schema_version_id,interpretation_id,source,definition,invalid_reason)
            VALUES (:id,:project,:version,:interpretation,'CARRIED_FORWARD',CAST(:definition AS jsonb),:reason)'''),
            {'id': uuid4(), 'project': project, 'version': new_version, 'interpretation': interpretation,
             'definition': json.dumps(definition, ensure_ascii=False), 'reason': reason})


def snapshot(database, project, schema_version):
    """Read all effective relations and their shared revision under the project lock."""
    with database.session() as session:
        lock_project(session, project)
        status = readiness(session, project, schema_version)
        if schema_version is None:
            return status | {'interpretation_id': None, 'ddl_hash': None, 'relations': []}
        state = version(session, project, schema_version)
        return status | {'interpretation_id': str(state['interpretation_id']) if state['interpretation_id'] else None,
                         'ddl_hash': state['manifest_hash'],
                         'relations': [item for item in relations(session, project, schema_version)
                                       if item['status'] == 'APPROVED']}


def discover(database, project, schema_version, request_id):
    with database.session() as session:
        lock_project(session, project)
        state = version(session, project, schema_version)
        if state['status'] != 'SUCCEEDED' or state['analysis'] is None:
            raise ProjectError(409, 'SCHEMA_ANALYSIS_NOT_READY', 'Schemat nie jest gotowy do analizy relacji.')
        existing = row(session, '''SELECT id FROM app.relation_discoveries WHERE project_id=:project
            AND schema_version_id=:version AND request_id=:request''', project=project, version=schema_version, request=request_id)
        if existing:
            return existing['id']
        id = uuid4()
        session.execute(text('''INSERT INTO app.relation_discoveries (id,project_id,schema_version_id,interpretation_id,request_id,status)
            VALUES (:id,:project,:version,:interpretation,:request,'PENDING')'''),
            {'id': id, 'project': project, 'version': schema_version, 'interpretation': state['interpretation_id'], 'request': request_id})
        return id


def discovery(database, project, schema_version, id):
    with database.session() as session:
        lock_project(session, project)
        record = row(session, '''SELECT id,status,error_code FROM app.relation_discoveries
            WHERE project_id=:project AND schema_version_id=:version AND id=:id''', project=project, version=schema_version, id=id)
        if record is None:
            raise ProjectError(404, 'RELATION_DISCOVERY_NOT_FOUND', 'Nie znaleziono prośby.')
        ids = {str(x) for x in session.execute(text('SELECT id FROM app.relation_proposals WHERE discovery_id=:id'), {'id': id}).scalars()}
        items = [p for p in relations(session, project, schema_version) if p['id'] in ids]
        return {'discovery_id': str(id), 'status': record['status'], 'items': items, 'error_code': record['error_code']}
