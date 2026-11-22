import pytest
from application_api.ddl_repository import PROFILE
from application_api.ddl_support import DdlSupport
from test_ddl_parser import parse


def analyze(sql):
    _, parsed = parse(sql.encode())
    return DdlSupport().diagnose(parsed, PROFILE)


@pytest.mark.parametrize(('sql', 'supported'), [
    ('CREATE TABLE t(id int PRIMARY KEY, parent int REFERENCES t(id));', True),
    ('CREATE TABLE t(id int PRIMARY KEY, parent int NOT NULL REFERENCES t(id));', False),
    ('CREATE TABLE t(a int, b int, PRIMARY KEY(a,b), x int, y int NOT NULL, FOREIGN KEY(x,y) REFERENCES t(a,b) MATCH SIMPLE);', True),
    ('CREATE TABLE t(a int, b int, PRIMARY KEY(a,b), x int, y int NOT NULL, FOREIGN KEY(x,y) REFERENCES t(a,b) MATCH FULL);', False),
    ('CREATE TABLE t(id int PRIMARY KEY, a int REFERENCES t(id), b int REFERENCES t(id));', False),
    ('CREATE TABLE a(id int PRIMARY KEY); CREATE TABLE b(id int PRIMARY KEY, a int REFERENCES a(id)); ALTER TABLE a ADD CONSTRAINT ab FOREIGN KEY(id) REFERENCES b(id);', False),
    ('CREATE TABLE a(id int PRIMARY KEY DEFERRABLE); CREATE TABLE b(id int REFERENCES a(id));', False),
    ('CREATE TABLE a(id int); CREATE TABLE b(id int REFERENCES a(id));', False),
    ('CREATE TABLE a(id int PRIMARY KEY); CREATE TABLE b(id int REFERENCES a(id));', True),
    ('CREATE SCHEMA a;', False),
    ('CREATE TABLE t(id int PRIMARY KEY, PRIMARY KEY(id));', False),
    ('CREATE TABLE t(a int, UNIQUE(a,a));', False),
])
def test_dependency_rules(sql, supported):
    result = analyze(sql)
    assert result.supported == supported, result.diagnostics


@pytest.mark.parametrize(('default', 'column', 'supported'), [
    ('32767', 'smallint', True), ('32768', 'smallint', False),
    ('32767.5', 'smallint', False), ('-32768.5', 'smallint', False),
    ('1::smallint', 'int', True), ("'bad'::uuid", 'uuid', False),
    ("'{A0EEBC99-9C0B-4EF8-BB6D-6BB9BD380A11}'", 'uuid', True),
    ('9.994', 'numeric(3,2)', True), ('9.995', 'numeric(3,2)', False),
    ("'abc '", 'varchar(3)', True), ("'abcd'", 'varchar(3)', False),
    ("'abcd'::varchar(3)", 'varchar(3)', True), ('NULL', 'int NOT NULL', True),
    ('CURRENT_DATE', 'timestamp', True),
])
def test_known_default_values(default, column, supported):
    result = analyze(f'CREATE TABLE t(a {column} DEFAULT {default});')
    assert result.supported == supported, result.diagnostics


def test_cycle_diagnostics_only_contain_internal_edges():
    result = analyze('''CREATE TABLE a(id int PRIMARY KEY);
        CREATE TABLE b(id int PRIMARY KEY, a int REFERENCES a(id));
        CREATE TABLE c(id int PRIMARY KEY, a int REFERENCES a(id));
        ALTER TABLE a ADD FOREIGN KEY(id) REFERENCES b(id);''')
    diagnostic = next(d for d in result.diagnostics if d.code == 'DDL_UNSUPPORTED_CYCLE')
    assert set(diagnostic.object_ids) == {r.constraint_id for r in result.relations if result.tables[2].table_id != r.source_table_id}


def test_chain_of_500_tables_does_not_recurse():
    sql = 'CREATE TABLE t0(id int PRIMARY KEY);' + ''.join(
        f'CREATE TABLE t{i}(id int PRIMARY KEY, p int REFERENCES t{i-1}(id));' for i in range(1, 500))
    assert analyze(sql).supported


@pytest.mark.parametrize('statement', [
    'CREATE TYPE mood AS ENUM (\'ok\');', 'CREATE DOMAIN amount AS int;',
    'CREATE EXTENSION hstore;', 'CREATE VIEW v AS SELECT 1;',
    'CREATE FUNCTION f() RETURNS int LANGUAGE sql AS $$ SELECT 1 $$;',
    'CREATE PROCEDURE p() LANGUAGE sql AS $$ SELECT 1 $$;',
    'CREATE TRIGGER x BEFORE INSERT ON t FOR EACH ROW EXECUTE FUNCTION f();',
    'CREATE FOREIGN TABLE x(a int) SERVER remote;', 'GRANT SELECT ON t TO public;',
    'ALTER TABLE t OWNER TO public;', 'INSERT INTO t VALUES (1);',
    'CREATE INDEX idx ON t(id);', "COMMENT ON TABLE t IS 'x';",
    'CREATE TABLE x(a int[]);', 'CREATE TABLE x(a json);', 'CREATE TABLE x(a jsonb);',
    'CREATE TABLE x(a int GENERATED ALWAYS AS (1) STORED);',
    'CREATE TABLE x(a int) PARTITION BY RANGE(a);', 'CREATE TABLE x() INHERITS (t);',
    'CREATE TABLE x(a int CHECK (abs(a) > 1));',
    'CREATE TABLE x(a int DEFAULT random());',
    'CREATE TABLE x(a int CHECK(a OPERATOR(public.=) 1));',
])
def test_excluded_groups_are_not_silently_accepted(statement):
    result = analyze('CREATE TABLE t(id int); ' + statement)
    assert not result.supported and any(d.severity == 'error' for d in result.diagnostics)


def test_named_default_diagnostic_points_to_default_token_after_comment():
    result = analyze('CREATE TABLE t(\n a smallint CONSTRAINT named /* comment */ DEFAULT 99999\n);')
    diagnostic = next(d for d in result.diagnostics if d.code == 'DDL_UNSUPPORTED_EXPRESSION')
    assert diagnostic.location.line == 2
    assert diagnostic.location.column == 44


def test_multiple_components_exclude_outside_edges_and_report_each_cycle():
    result = analyze('''
        CREATE TABLE a(id int PRIMARY KEY);
        CREATE TABLE b(id int PRIMARY KEY, a int REFERENCES a(id));
        ALTER TABLE a ADD FOREIGN KEY(id) REFERENCES b(id);
        CREATE TABLE c(id int PRIMARY KEY, a int REFERENCES a(id));
        CREATE TABLE d(id int PRIMARY KEY, c int REFERENCES c(id));
        ALTER TABLE c ADD FOREIGN KEY(id) REFERENCES d(id);
        CREATE TABLE e(id int PRIMARY KEY, d int REFERENCES d(id));
    ''')
    diagnostics = [d for d in result.diagnostics if d.code == 'DDL_UNSUPPORTED_CYCLE']
    assert len(diagnostics) == 2
    assert [len(d.object_ids) for d in diagnostics] == [2, 2]
    assert all(d.location is not None for d in diagnostics)


def test_deferred_nullable_three_table_cycle_still_blocks():
    result = analyze('''
        CREATE TABLE a(id int PRIMARY KEY, p int);
        CREATE TABLE b(id int PRIMARY KEY, p int REFERENCES a(id) DEFERRABLE INITIALLY DEFERRED);
        CREATE TABLE c(id int PRIMARY KEY, p int REFERENCES b(id));
        ALTER TABLE a ADD FOREIGN KEY(p) REFERENCES c(id);
    ''')
    diagnostic = next(d for d in result.diagnostics if d.code == 'DDL_UNSUPPORTED_CYCLE')
    assert len(diagnostic.object_ids) == 3


@pytest.mark.parametrize(('sql', 'supported', 'code'), [
    ('CREATE TABLE t(a bigint DEFAULT 0x80000000);', True, None),
    ('CREATE TABLE t(a numeric DEFAULT 0x8000000000000000);', True, None),
    ('CREATE TABLE t(a bigint DEFAULT 0b10000000000000000000000000000000);', True, None),
    ('CREATE TABLE t(a bigint DEFAULT 0o20000000000);', True, None),
    ('CREATE TABLE t(a bigint DEFAULT 0x8000000000000000);', False, 'DDL_UNSUPPORTED_EXPRESSION'),
    ('CREATE TABLE t(a numeric(3,0) DEFAULT 0x100000000);', False, 'DDL_UNSUPPORTED_EXPRESSION'),
    ('CREATE TABLE t(a numeric(30,0) DEFAULT 1e1000000);', False, 'DDL_UNSUPPORTED_EXPRESSION'),
    ('CREATE TABLE t(a numeric DEFAULT 1e1000000);', False, 'DDL_UNSUPPORTED_EXPRESSION'),
    ("CREATE TABLE t(a numeric DEFAULT 'sNaN');", False, 'DDL_UNSUPPORTED_EXPRESSION'),
    ("CREATE TABLE t(a integer DEFAULT '0xFF');", True, None),
    ('CREATE TABLE t(a numeric(1000000,0) DEFAULT 1);', False, 'DDL_UNSUPPORTED_TYPE'),
    ('CREATE TABLE t(a numeric(30,0) DEFAULT 999999999999999999999999999999);', True, None),
    ("CREATE TABLE t(a uuid DEFAULT ' 00000000-0000-0000-0000-000000000001 ');", False, 'DDL_UNSUPPORTED_EXPRESSION'),
    ('CREATE TABLE a(id int); CREATE TABLE b(id int REFERENCES a(id)); ALTER TABLE a ADD UNIQUE(id);', False, 'DDL_UNRESOLVED_REFERENCE'),
    ('CREATE TABLE a(id int PRIMARY KEY DEFERRABLE, UNIQUE(id)); CREATE TABLE b(id int REFERENCES a);', False, 'DDL_UNRESOLVED_REFERENCE'),
    ('CREATE TABLE a(id int, parent int, FOREIGN KEY(parent) REFERENCES a(id), PRIMARY KEY(id));', True, None),
])
def test_review_regressions_through_production_worker(tmp_path, sql, supported, code):
    import base64

    from application_api.ddl_process import WorkerProcess
    from test_ddl_parser import bundle_for

    content = sql.encode()
    bundle = bundle_for(content)
    request = {'bundle': bundle.model_dump(mode='json'), 'profile': PROFILE.model_dump(mode='json'),
               'files_base64': [base64.b64encode(content).decode()], 'checkpoint': None}
    outcome = WorkerProcess(tmp_path).run(request)
    assert outcome.error is None
    result = outcome.messages[-1]
    assert result['type'] == 'result'
    assert result['analysis']['supported'] == supported
    if code:
        assert code in [item['code'] for item in result['analysis']['diagnostics']]


def test_default_error_location_in_second_file():
    bundle, parsed = parse(b'CREATE TABLE t(id int, v int CONSTRAINT named',
                           b'\xef\xbb\xbf/* comment */\r\nDEFAULT id);')
    diagnostic = next(d for d in parsed.diagnostics if d.code == 'DDL_UNSUPPORTED_EXPRESSION')
    assert diagnostic.location.file_id == bundle.files[1].file_id
    assert diagnostic.location.line == 2
    assert diagnostic.location.column == 1


@pytest.mark.parametrize('key', ['UNIQUE(id)', 'PRIMARY KEY(id)'])
def test_alter_foreign_key_can_use_key_in_same_statement(key):
    reference = 't(id)' if key.startswith('UNIQUE') else 't'
    result = analyze('CREATE TABLE t(id int, parent int); '
                     f'ALTER TABLE t ADD FOREIGN KEY(parent) REFERENCES {reference}, ADD {key};')
    assert result.supported, result.diagnostics


@pytest.mark.parametrize(('type_name', 'value', 'supported'), [
    ('integer', "'0xFF'", True), ('integer', "'-0xFF'", True),
    ('integer', "'1_000'", True), ('integer', "'0b101'", True),
    ('integer', "'0o77'", True), ('integer', "'0x_FF'", True),
    ('integer', "'1__0'", False), ('integer', "'1_'", False),
    ('numeric', "'0xFF'", True), ('numeric', "'1_000'", True),
    ('numeric', "'1_2.3_4e+1_0'", True), ('numeric', "'sNaN'", False),
    ('numeric', '1e1000000', False), ('numeric', '1e-1000000', False),
    ('numeric', '1e131071', True), ('numeric', '1e131072', False),
    ('numeric', '1e-16383', True), ('numeric', '1e-16384', False),
])
def test_numeric_literals_follow_postgres_18_limits(type_name, value, supported):
    result = analyze(f'CREATE TABLE t(a {type_name} DEFAULT {value});')
    assert result.supported == supported, result.diagnostics


@pytest.mark.parametrize(('prefix', 'digit', 'count'), [('0x', 'f', 109000), ('0o', '7', 146000), ('0b', '1', 436000)])
def test_excessive_base_literal_is_rejected_before_integer_conversion(prefix, digit, count):
    from application_api.ddl_support import parse_number

    with pytest.raises(ValueError, match='numeric value exceeds'):
        parse_number(prefix + digit * count, 'numeric', 'numeric')


def test_leading_zeroes_do_not_count_towards_numeric_base_limit():
    from application_api.ddl_support import parse_number

    assert parse_number('0x' + '0' * 109000 + 'ff', 'numeric', 'numeric') == 255
