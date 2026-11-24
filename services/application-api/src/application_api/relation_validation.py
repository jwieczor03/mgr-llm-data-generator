"""Validate proposed references against a pinned schema and its effective graph."""
from application_api.schema_contracts import SchemaAnalysis


def duplicates_ddl(analysis: SchemaAnalysis, proposal: dict) -> bool:
    pairs = {(p['source_column_id'], p['target_column_id']) for p in proposal['column_pairs']}
    return any(str(r.source_table_id) == proposal['source_table_id']
               and str(r.target_table_id) == proposal['target_table_id']
               and {(str(a), str(b)) for a, b in r.column_pairs} == pairs for r in analysis.relations)


def definition_error(analysis: SchemaAnalysis, proposal: dict, effective: list[dict], required: bool | None = None) -> str | None:
    tables = {str(t.table_id): t for t in analysis.tables}
    columns = {str(c.column_id): c for c in analysis.columns}
    source, target = proposal['source_table_id'], proposal['target_table_id']
    pairs = proposal['column_pairs']
    if source not in tables or target not in tables or not pairs:
        return 'Nie znaleziono tabeli lub par kolumn.'
    sources = [p['source_column_id'] for p in pairs]
    targets = [p['target_column_id'] for p in pairs]
    if len(set(sources)) != len(sources) or len(set(targets)) != len(targets):
        return 'Kolumna występuje w relacji więcej niż raz.'
    if any(s not in columns or t not in columns or str(columns[s].table_id) != source
           or str(columns[t].table_id) != target for s, t in zip(sources, targets)):
        return 'Nie znaleziono kolumn relacji w odpowiednich tabelach.'
    if duplicates_ddl(analysis, proposal):
        return 'Relacja jest już zadeklarowana jako klucz obcy w DDL.'
    groups = ({'smallint', 'integer', 'bigint', 'numeric'}, {'text', 'varchar'})
    def compatible(a, b):
        return a == b and a in {'smallint', 'integer', 'bigint', 'numeric', 'text', 'varchar',
                                'boolean', 'uuid', 'date', 'timestamp', 'timestamptz'} or any(a in g and b in g for g in groups)
    if any(not compatible(columns[s].type.name, columns[t].type.name) for s, t in zip(sources, targets)):
        return 'Typy kolumn relacji są niezgodne.'
    if not any(str(c.table_id) == target and c.kind in ('primary_key', 'unique')
               and set(map(str, c.column_ids)) == set(targets) for c in analysis.constraints):
        return 'Kolumny docelowe nie tworzą klucza głównego ani unikalnego.'
    edges = [(str(r.source_table_id), str(r.target_table_id)) for r in analysis.relations]
    edges += [(r['source_table_id'], r['target_table_id']) for r in effective]
    if source == target:
        if required is True or any(not columns[s].nullable for s in sources) or (source, target) in edges:
            return 'Hierarchia wymaga jednego opcjonalnego odwołania z kolumnami nullable.'
    else:
        adjacency = {}
        for a, b in edges:
            if a != b:
                adjacency.setdefault(a, set()).add(b)
        pending, seen = [target], set()
        while pending:
            node = pending.pop()
            if node == source:
                return 'Relacja tworzy nieobsługiwany cykl między tabelami.'
            if node not in seen:
                seen.add(node)
                pending.extend(adjacency.get(node, ()))
    return None
