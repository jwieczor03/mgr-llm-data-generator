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
