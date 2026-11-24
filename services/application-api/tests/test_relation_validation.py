from application_api.ddl_parser import DdlParser
from application_api.ddl_repository import PROFILE
from application_api.ddl_support import DdlSupport
from application_api.relation_validation import definition_error
from test_ddl_parser import bundle_for


def schema(sql):
    content = sql.encode()
    bundle = bundle_for(content)
    parsed = DdlParser(lambda _: content).parse(bundle, PROFILE)
    return DdlSupport().diagnose(parsed, PROFILE)


def proposal(analysis, source, target, pairs):
    tables = {t.name: t for t in analysis.tables}
    columns = {(str(c.table_id), c.name): str(c.column_id) for c in analysis.columns}
    a, b = str(tables[source].table_id), str(tables[target].table_id)
    return {'source_table_id': a, 'target_table_id': b, 'column_pairs': [
        {'source_column_id': columns[(a, x)], 'target_column_id': columns[(b, y)]} for x, y in pairs]}


def test_composite_unique_types_and_graph():
    a = schema('CREATE TABLE p (a int, b text, UNIQUE (b,a)); CREATE TABLE c (a bigint, b varchar(4));')
    p = proposal(a, 'c', 'p', [('a', 'a'), ('b', 'b')])
    assert definition_error(a, p, []) is None
    assert definition_error(a, p | {'column_pairs': p['column_pairs'][:1]}, [])
    cycle = {'source_table_id': p['target_table_id'], 'target_table_id': p['source_table_id']}
    assert definition_error(a, p, [cycle])


def test_self_reference_requires_nullable_and_optional():
    a = schema('CREATE TABLE t (id int PRIMARY KEY, parent_id int);')
    p = proposal(a, 't', 't', [('parent_id', 'id')])
    assert definition_error(a, p, [], False) is None
    assert definition_error(a, p, [], True)
    assert definition_error(a, p, [p], False)
    b = schema('CREATE TABLE t (id int PRIMARY KEY, parent_id int NOT NULL);')
    assert definition_error(b, proposal(b, 't', 't', [('parent_id', 'id')]), [], False)


def test_reordered_composite_ddl_fk_is_same_relation():
    a = schema('CREATE TABLE p (a int, b int, PRIMARY KEY(a,b)); '
               'CREATE TABLE c (x int, y int, FOREIGN KEY(x,y) REFERENCES p(a,b));')
    reordered = proposal(a, 'c', 'p', [('y', 'b'), ('x', 'a')])
    assert 'DDL' in definition_error(a, reordered, [])
    different = proposal(a, 'c', 'p', [('y', 'a'), ('x', 'b')])
    assert definition_error(a, different, []) is None
