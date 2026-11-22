import base64
import hashlib
from uuid import uuid4

import pytest
from application_api.ddl_parser import DdlParser
from application_api.ddl_repository import PROFILE
from application_api.ddl_worker_analysis import analyze
from application_api.schema_contracts import (
    Checkpoint,
    DdlBundle,
    ManifestFile,
    manifest_digest,
)


def bundle_for(*contents):
    files = [ManifestFile(file_id=uuid4(), name=f'{i}.sql', position=i, size_bytes=len(data),
                          sha256=hashlib.sha256(data).hexdigest(), artifact_id=uuid4())
             for i, data in enumerate(contents)]
    return DdlBundle(schema_version_id=uuid4(), manifest_hash=manifest_digest(files), files=files)


def parse(*contents):
    bundle = bundle_for(*contents)
    parsed = DdlParser(lambda file: contents[file.position]).parse(bundle, PROFILE)
    return bundle, parsed


def test_multifile_schema_constraints_and_positions():
    first = '\ufeffCREATE SCHEMA a; SET search_path TO a, public;\r\nCREATE TABLE "Rodzic" (a int, b int, PRIMARY KEY(a,b));\r\nCREATE TABLE "Dziecko" ('.encode()
    second = '\ufeffx int, y int, CHECK (x BETWEEN 1 AND 4), FOREIGN KEY (x,y) REFERENCES "Rodzic" (a,b) MATCH FULL ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED);'.encode()
    bundle, result = parse(first, second)
    assert result.diagnostics == []
    assert [(t.schema_name, t.name) for t in result.tables] == [('a', 'Rodzic'), ('a', 'Dziecko')]
    assert len(result.relations[0].column_pairs) == 2
    assert (result.relations[0].match, result.relations[0].on_delete, result.relations[0].deferrable, result.relations[0].initially_deferred) == ('full', 'set_null', True, True)
    assert result.columns[-1].location.file_id == bundle.files[1].file_id
    check = next(c for c in result.constraints if c.kind == 'check')
    assert check.expression.op == 'between'
    assert check.expression.original == 'x BETWEEN 1 AND 4'
    assert check.expression.original_scope == 'expression'


def test_column_fk_deferrability_and_unsupported_expression():
    _, result = parse(b'CREATE TABLE p (id int PRIMARY KEY); CREATE TABLE c (id int REFERENCES p(id) DEFERRABLE INITIALLY DEFERRED, v int CHECK (abs(v) > 0));')
    assert result.relations[0].deferrable and result.relations[0].initially_deferred
    assert [d.code for d in result.diagnostics] == ['DDL_UNSUPPORTED_EXPRESSION']
    assert next(c for c in result.constraints if c.kind == 'check').expression.op == 'unsupported'


def test_corrupted_manifest_is_technical_failure():
    bundle = bundle_for(b'CREATE TABLE t (id int);')
    with pytest.raises(ValueError, match='differs'):
        DdlParser(lambda _: b'other').parse(bundle, PROFILE)


def test_worker_checkpoint_and_resume():
    content = b'CREATE TABLE t (id int);'
    bundle = bundle_for(content)
    request = {'bundle': bundle.model_dump(mode='json'), 'profile': PROFILE.model_dump(mode='json'),
               'files_base64': [base64.b64encode(content).decode()], 'checkpoint': None}
    messages = []
    assert analyze(request, messages.append)['code'] == 'DDL_ANALYZER_UNAVAILABLE'
    assert len(messages) == 1
    checkpoint = Checkpoint.model_validate(messages[0]['checkpoint'])
    assert checkpoint.valid_for(bundle, PROFILE)
    request['checkpoint'] = messages[0]['checkpoint']
    messages.clear()
    assert analyze(request, messages.append)['code'] == 'DDL_ANALYZER_UNAVAILABLE'
    assert messages == []


def test_original_expressions_keep_spacing_comments_and_nested_commas():
    _, result = parse(b"CREATE TABLE t (a text DEFAULT 'a,b' /* test */ NOT NULL, b numeric DEFAULT (1.20::numeric(5,2)) UNIQUE, c int CONSTRAINT ck CHECK ( c IN (1, 2) /* ok */ ));")
    assert result.diagnostics == []
    assert result.columns[0].default.original == "'a,b' /* test */"
    assert result.columns[1].default.original == '(1.20::numeric(5,2))'
    expr = next(c.expression for c in result.constraints if c.kind == 'check')
    assert expr.original == ' c IN (1, 2) /* ok */ '
    assert expr.original_scope == 'expression'


def test_quoted_names_and_unsupported_statement():
    _, result = parse('CREATE TABLE "Zażółć" ("MiXeD" text); CREATE VIEW v AS SELECT 1;'.encode())
    assert result.tables[0].original_name == '"Zażółć"'
    assert result.columns[0].original_name == '"MiXeD"'
    assert result.diagnostics[-1].code == 'DDL_UNSUPPORTED_STATEMENT'


def test_default_arbitrary_expression_is_diagnosed():
    _, result = parse(b"CREATE TABLE t (a int DEFAULT 1 + 2, b int DEFAULT nextval('s'));")
    assert [d.code for d in result.diagnostics] == ['DDL_UNSUPPORTED_EXPRESSION'] * 2
    assert all(c.default.op == 'unsupported' for c in result.columns)



def test_types_identity_alter_composite_and_default():
    sql = b'''CREATE TABLE p (a smallint, b integer, PRIMARY KEY (a,b));
    CREATE TABLE t (a smallint, b integer, c bigint, d numeric(12,3), e decimal(9,2),
      f text, g varchar(42), h boolean, i uuid, j date DEFAULT CURRENT_DATE,
      k timestamp, l timestamptz DEFAULT CURRENT_TIMESTAMP, m serial, n bigserial,
      o integer GENERATED ALWAYS AS IDENTITY, q bigint GENERATED BY DEFAULT AS IDENTITY);
    ALTER TABLE ONLY t ADD CONSTRAINT uq UNIQUE (a,b);
    ALTER TABLE ONLY t ADD CONSTRAINT fk FOREIGN KEY (a,b) REFERENCES p(a,b)
      MATCH SIMPLE ON UPDATE CASCADE ON DELETE SET DEFAULT NOT DEFERRABLE INITIALLY IMMEDIATE;
    ALTER TABLE ONLY t ADD CONSTRAINT ck CHECK (a >= 0 AND (b IN (1,2) OR NOT b BETWEEN 3 AND 4));'''
    _, result = parse(sql)
    assert result.diagnostics == []
    cols = result.columns[2:]
    assert [c.type.name for c in cols] == ['smallint', 'integer', 'bigint', 'numeric', 'numeric', 'text', 'varchar', 'boolean', 'uuid', 'date', 'timestamp', 'timestamptz', 'integer', 'bigint', 'integer', 'bigint']
    assert (cols[3].type.precision, cols[3].type.scale, cols[6].type.length) == (12, 3, 42)
    assert [c.automatic_id for c in cols[-4:]] == ['serial', 'bigserial', 'identity_always', 'identity_by_default']
    assert (cols[9].default.op, cols[11].default.op) == ('current_date', 'current_timestamp')
    relation = result.relations[0]
    assert len(relation.column_pairs) == 2
    assert (relation.match, relation.on_update, relation.on_delete, relation.deferrable, relation.initially_deferred) == ('simple', 'cascade', 'set_default', False, False)


def test_unresolved_forward_and_unknown_types_and_options_are_diagnosed():
    _, result = parse(b'CREATE TABLE t (id int REFERENCES later(id), x int[]); CREATE TABLE later (id int PRIMARY KEY); CREATE TABLE generated (x int GENERATED ALWAYS AS (2) STORED);')
    codes = [d.code for d in result.diagnostics]
    assert 'DDL_UNSUPPORTED_TYPE' in codes
    assert 'DDL_UNRESOLVED_REFERENCE' in codes
    assert 'DDL_UNSUPPORTED_STATEMENT' in codes


def test_syntax_error_position_utf8_crlf_and_second_file():
    _, result = parse('CREATE TABLE "żółć" (id int);\r\n'.encode(), '\ufeffCREATE TABLE t (\r\n x ???\r\n);'.encode())
    diag = result.diagnostics[0]
    assert diag.code == 'DDL_SYNTAX_ERROR'
    assert (diag.location.line, diag.location.column) == (2, 4)


def test_defaults_keep_sql_syntax_without_guessing_postgres_conversion():
    _, result = parse(b"CREATE TABLE t (a uuid DEFAULT 'abc'::uuid, b integer DEFAULT 2147483648, c date DEFAULT '2026-11-21', d integer DEFAULT 1::smallint, e timestamp DEFAULT CURRENT_DATE, f int NOT NULL DEFAULT NULL);")
    assert result.diagnostics == []
    defaults = [column.default for column in result.columns]
    assert defaults[0].target_type.name == 'uuid'
    assert (defaults[1].literal_type, defaults[1].literal_value) == ('integer', '2147483648')
    assert defaults[2].literal_value == '2026-11-21'
    assert defaults[3].target_type.name == 'smallint'
    assert defaults[4].op == 'current_date'
    assert defaults[5].literal_type == 'null'
    assert not result.columns[5].nullable


FK_OPTIONS = [('', None), ('MATCH SIMPLE', ('match', 'simple')), ('MATCH FULL', ('match', 'full'))]
FK_OPTIONS += [(f'ON {event} {sql}', (attribute, value))
               for event, attribute in [('DELETE', 'on_delete'), ('UPDATE', 'on_update')]
               for sql, value in [('NO ACTION', 'no_action'), ('RESTRICT', 'restrict'),
                                  ('CASCADE', 'cascade'), ('SET NULL', 'set_null'),
                                  ('SET DEFAULT', 'set_default')]]
FK_OPTIONS += [('DEFERRABLE', ('deferrable', True)), ('NOT DEFERRABLE', ('deferrable', False)),
               ('DEFERRABLE INITIALLY DEFERRED', ('initially_deferred', True)),
               ('DEFERRABLE INITIALLY IMMEDIATE', ('initially_deferred', False)),
               ('NOT DEFERRABLE INITIALLY IMMEDIATE', ('deferrable', False))]


@pytest.mark.parametrize('form', ['column', 'table', 'alter'])
@pytest.mark.parametrize(('clause', 'expected'), FK_OPTIONS)
def test_foreign_key_options_matrix(form, clause, expected):
    reference = 'REFERENCES parent(id) ' + clause
    child = {'column': f'CREATE TABLE child (id int {reference});',
             'table': f'CREATE TABLE child (id int, FOREIGN KEY(id) {reference});',
             'alter': f'CREATE TABLE child (id int); ALTER TABLE ONLY child ADD CONSTRAINT fk FOREIGN KEY(id) {reference};'}[form]
    _, result = parse(('CREATE TABLE parent (id int PRIMARY KEY); ' + child).encode())
    assert result.diagnostics == []
    assert len(result.relations) == 1
    fk = next(c for c in result.constraints if c.kind == 'foreign_key')
    assert (fk.deferrable, fk.initially_deferred) == (result.relations[0].deferrable, result.relations[0].initially_deferred)
    if expected:
        assert getattr(result.relations[0], expected[0]) == expected[1]


def test_self_reference_can_use_primary_key_declared_later_in_same_table():
    _, result = parse(b'CREATE TABLE tree (id int, parent int REFERENCES tree, PRIMARY KEY (id));')
    assert result.diagnostics == []
    assert result.relations[0].source_table_id == result.relations[0].target_table_id
    assert result.relations[0].column_pairs == [(result.columns[1].column_id, result.columns[0].column_id)]


@pytest.mark.parametrize('kind', ['PRIMARY KEY', 'UNIQUE'])
@pytest.mark.parametrize('form', ['column', 'table', 'alter'])
@pytest.mark.parametrize(('clause', 'deferred', 'initial'), [
    ('', False, False), ('NOT DEFERRABLE', False, False),
    ('DEFERRABLE', True, False), ('DEFERRABLE INITIALLY IMMEDIATE', True, False),
    ('DEFERRABLE INITIALLY DEFERRED', True, True),
])
def test_primary_and_unique_deferral_matrix(kind, form, clause, deferred, initial):
    sql = {'column': f'CREATE TABLE t (id int {kind} {clause});',
           'table': f'CREATE TABLE t (id int, {kind}(id) {clause});',
           'alter': f'CREATE TABLE t (id int); ALTER TABLE ONLY t ADD CONSTRAINT k {kind}(id) {clause};'}[form]
    _, result = parse(sql.encode())
    assert result.diagnostics == []
    constraint = result.constraints[0]
    assert (constraint.deferrable, constraint.initially_deferred) == (deferred, initial)


def test_check_qualified_column_is_resolved_to_its_id():
    _, result = parse(b'CREATE TABLE t (id int, CHECK (t.id > 0));')
    assert result.diagnostics == []
    check = result.constraints[0]
    assert check.column_ids == [result.columns[0].column_id]
    assert check.expression.args[0].column_id == result.columns[0].column_id


def test_unrecognized_storage_and_column_options_are_not_silently_accepted():
    _, result = parse(b'CREATE TABLE t (a text COLLATE "C"); CREATE TABLE u (a int) TABLESPACE custom;')
    assert [d.code for d in result.diagnostics] == ['DDL_UNSUPPORTED_STATEMENT', 'DDL_UNSUPPORTED_STATEMENT']


def test_quoted_table_names_in_separate_schemas_remain_distinct():
    _, result = parse(b'CREATE SCHEMA a; CREATE SCHEMA b; CREATE TABLE a."Orders" ("ID" int); CREATE TABLE b."Orders" ("ID" int);')
    assert result.diagnostics == []
    assert [(table.schema_name, table.name, table.original_name) for table in result.tables] == [
        ('a', 'Orders', '"Orders"'), ('b', 'Orders', '"Orders"')]
    assert result.tables[0].table_id != result.tables[1].table_id


def test_checkpoint_hash_covers_expression_scope_and_deferral():
    content = b'CREATE TABLE t (a int UNIQUE DEFERRABLE INITIALLY DEFERRED, b int CHECK (b > 0));'
    bundle = bundle_for(content)
    request = {'bundle': bundle.model_dump(mode='json'), 'profile': PROFILE.model_dump(mode='json'),
               'files_base64': [base64.b64encode(content).decode()], 'checkpoint': None}
    messages = []
    analyze(request, messages.append)
    checkpoint = Checkpoint.model_validate(messages[0]['checkpoint'])
    assert checkpoint.valid_for(bundle, PROFILE)
    modified = checkpoint.model_dump(mode='json')
    modified['parsed']['constraints'][0]['deferrable'] = False
    assert not Checkpoint.model_validate(modified).valid_for(bundle, PROFILE)
    modified = checkpoint.model_dump(mode='json')
    modified['parsed']['constraints'][1]['expression']['original_scope'] = 'statement'
    assert not Checkpoint.model_validate(modified).valid_for(bundle, PROFILE)


def test_fk_does_not_drop_missing_target_column():
    _, result = parse(b'CREATE TABLE p(id int PRIMARY KEY); CREATE TABLE t(a int REFERENCES p(id, missing));')
    assert any(d.code == 'DDL_UNRESOLVED_REFERENCE' for d in result.diagnostics)
    assert result.relations == []


@pytest.mark.parametrize('sql', [
    b'CREATE TABLE t(a int); ALTER TABLE t ADD CONSTRAINT pk PRIMARY KEY USING INDEX idx;',
    b'CREATE TABLE t(a int, UNIQUE(a) USING INDEX TABLESPACE ts);',
    b'CREATE TABLE t(a int, UNIQUE(a WITHOUT OVERLAPS));',
    b'CREATE TABLE t(a text STORAGE EXTERNAL);',
    b'CREATE TABLE t(a int); ALTER FOREIGN TABLE t ADD CONSTRAINT c CHECK (a > 1);',
])
def test_unsupported_ast_attributes_are_diagnosed(sql):
    _, result = parse(sql)
    assert any(d.code == 'DDL_UNSUPPORTED_STATEMENT' for d in result.diagnostics)
    assert not any(c.kind == 'primary_key' and not c.column_ids for c in result.constraints)


@pytest.mark.parametrize('kind', ['PRIMARY KEY', 'UNIQUE', 'FOREIGN KEY'])
@pytest.mark.parametrize('form', ['column', 'table', 'alter'])
def test_initially_deferred_implies_deferrable_in_all_forms(kind, form):
    column_kind = 'REFERENCES p(id)' if kind == 'FOREIGN KEY' else kind
    table_kind = 'FOREIGN KEY (a) REFERENCES p(id)' if kind == 'FOREIGN KEY' else f'{kind} (a)'
    statement = {
        'column': f'CREATE TABLE t(a int {column_kind} INITIALLY DEFERRED);',
        'table': f'CREATE TABLE t(a int, {table_kind} INITIALLY DEFERRED);',
        'alter': f'CREATE TABLE t(a int); ALTER TABLE t ADD CONSTRAINT c {table_kind} INITIALLY DEFERRED;',
    }[form]
    _, result = parse(('CREATE TABLE p(id int PRIMARY KEY); ' + statement).encode())
    assert result.diagnostics == []
    c = next(c for c in result.constraints if c.table_id == result.tables[1].table_id)
    assert (c.deferrable, c.initially_deferred) == (True, True)
    if result.relations:
        assert (result.relations[0].deferrable, result.relations[0].initially_deferred) == (True, True)


def test_invalid_numeric_precision_is_content_diagnostic():
    _, result = parse(b'CREATE TABLE t(a numeric(-1));')
    assert [d.code for d in result.diagnostics] == ['DDL_UNSUPPORTED_TYPE']


def test_unsupported_default_never_marks_truncated_case_as_complete():
    sql = b'CREATE TABLE t(a int DEFAULT CASE WHEN true THEN NULL ELSE 1 END);'
    _, result = parse(sql)
    default = result.columns[0].default
    assert default.op == 'unsupported'
    assert default.original_scope == 'statement'
    assert default.original == sql.decode().rstrip(';')


@pytest.mark.parametrize('sql', [
    b'CREATE TABLE t(a int DEFAULT 1 DEFAULT 2);',
    b'CREATE TABLE t(a int GENERATED ALWAYS AS IDENTITY GENERATED BY DEFAULT AS IDENTITY);',
])
def test_duplicate_default_and_identity_are_diagnosed_without_overwrite(sql):
    _, result = parse(sql)
    assert any(d.code == 'DDL_UNSUPPORTED_STATEMENT' for d in result.diagnostics)
    column = result.columns[0]
    if column.default is not None:
        assert column.default.literal_value == '1'
    else:
        assert column.automatic_id == 'identity_always'


@pytest.mark.parametrize('declaration', [
    'FOREIGN KEY (a,b) REFERENCES p(x,missing)',
    'FOREIGN KEY (a,b) REFERENCES p(x)',
    'FOREIGN KEY (a) REFERENCES p(x,y)',
])
def test_composite_fk_invalid_target_never_emits_partial_relation(declaration):
    sql = f'CREATE TABLE p(x int, y int, PRIMARY KEY(x,y)); CREATE TABLE t(a int, b int, {declaration});'
    _, result = parse(sql.encode())
    assert any(d.code == 'DDL_UNRESOLVED_REFERENCE' for d in result.diagnostics)
    assert result.relations == []


def test_invalid_numeric_precision_produces_real_worker_checkpoint(tmp_path):
    from application_api.ddl_process import WorkerProcess

    content = b'CREATE TABLE t(a numeric(-1));'
    bundle = bundle_for(content)
    request = {'bundle': bundle.model_dump(mode='json'), 'profile': PROFILE.model_dump(mode='json'),
               'files_base64': [base64.b64encode(content).decode()], 'checkpoint': None}
    outcome = WorkerProcess(tmp_path).run(request)
    assert outcome.error is None
    assert [message['type'] for message in outcome.messages] == ['checkpoint', 'error']
    checkpoint = Checkpoint.model_validate(outcome.messages[0]['checkpoint'])
    assert checkpoint.valid_for(bundle, PROFILE)
    assert [diagnostic.code for diagnostic in checkpoint.parsed.diagnostics] == ['DDL_UNSUPPORTED_TYPE']
    assert outcome.messages[1]['code'] == 'DDL_ANALYZER_UNAVAILABLE'


def test_conflicting_not_deferrable_initially_deferred_is_diagnosed():
    _, result = parse(b'CREATE TABLE t(a int UNIQUE NOT DEFERRABLE INITIALLY DEFERRED);')
    assert any(d.code == 'DDL_UNSUPPORTED_STATEMENT' for d in result.diagnostics)


def test_numeric_negative_scale_remains_supported():
    _, result = parse(b'CREATE TABLE t(a numeric(5,-1));')
    assert result.diagnostics == []
    assert (result.columns[0].type.precision, result.columns[0].type.scale) == (5, -1)
