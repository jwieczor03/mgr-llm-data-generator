"""Assess whether the parsed schema belongs to the supported MVP profile."""
import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, localcontext

from application_api.schema_contracts import Diagnostic, SchemaAnalysis


class DdlSupport:
    def diagnose(self, parsed, profile):
        diagnostics = list(parsed.diagnostics)
        constraints = {c.constraint_id: c for c in parsed.constraints}
        columns = {c.column_id: c for c in parsed.columns}

        def error(code, message, ids=(), location=None):
            diagnostics.append(Diagnostic(code=code, message=message, severity='error',
                                          scope='object' if ids else 'bundle',
                                          object_ids=list(ids), location=location))

        if not parsed.tables and not any(d.severity == 'error' for d in diagnostics):
            error('DDL_UNSUPPORTED_STATEMENT', 'The bundle contains no tables')
        keys = {}
        for c in parsed.constraints:
            if c.kind in {'primary_key', 'unique'} and not c.deferrable:
                keys.setdefault(c.table_id, set()).add(frozenset(c.column_ids))
        for relation in parsed.relations:
            target = [pair[1] for pair in relation.column_pairs]
            if frozenset(target) not in keys.get(relation.target_table_id, set()):
                c = constraints[relation.constraint_id]
                error('DDL_UNRESOLVED_REFERENCE', 'Foreign key requires a non-deferrable target key',
                      [c.constraint_id], c.location)

        for column in parsed.columns:
            if column.default and not valid_default_value(column.default, column.type):
                error('DDL_UNSUPPORTED_EXPRESSION', 'DEFAULT value is invalid for its type',
                      [column.column_id], column.default_location)

        self_relations = {}
        edges = {table.table_id: [] for table in parsed.tables}
        reverse = {table.table_id: [] for table in parsed.tables}
        for relation in parsed.relations:
            if relation.source_table_id == relation.target_table_id:
                self_relations.setdefault(relation.source_table_id, []).append(relation)
            else:
                edges[relation.source_table_id].append(relation.target_table_id)
                reverse[relation.target_table_id].append(relation.source_table_id)
        for relations in self_relations.values():
            if len(relations) > 1:
                ids = [r.constraint_id for r in relations]
                error('DDL_UNSUPPORTED_CYCLE', 'Multiple self-referencing foreign keys are unsupported',
                      ids, constraints[ids[1]].location)
                continue
            relation = relations[0]
            nullable = [columns[source].nullable for source, _ in relation.column_pairs]
            root_possible = all(nullable) if relation.match == 'full' else any(nullable)
            if not root_possible:
                c = constraints[relation.constraint_id]
                error('DDL_UNSUPPORTED_CYCLE', 'Self-reference does not permit a root', [c.constraint_id], c.location)

        # Iterative Kosaraju avoids Python recursion limits for large schemas.
        visited, order = set(), []
        for node in edges:
            if node in visited:
                continue
            visited.add(node)
            stack = [(node, iter(edges[node]))]
            while stack:
                current, neighbours = stack[-1]
                neighbour = next(neighbours, None)
                if neighbour is None:
                    order.append(current)
                    stack.pop()
                elif neighbour not in visited:
                    visited.add(neighbour)
                    stack.append((neighbour, iter(edges[neighbour])))
        components, membership = [], {}
        for node in reversed(order):
            if node in membership:
                continue
            index = len(components)
            component, stack = [], [node]
            membership[node] = index
            while stack:
                current = stack.pop()
                component.append(current)
                for neighbour in reverse[current]:
                    if neighbour not in membership:
                        membership[neighbour] = index
                        stack.append(neighbour)
            components.append(component)
        internal = [[] for _ in components]
        for relation in parsed.relations:
            source, target = relation.source_table_id, relation.target_table_id
            if source != target and membership[source] == membership[target]:
                internal[membership[source]].append(relation.constraint_id)
        for ids in internal:
            if ids:
                error('DDL_UNSUPPORTED_CYCLE', 'Circular dependency between tables is unsupported',
                      ids, constraints[ids[0]].location)
        data = parsed.model_dump(exclude={'diagnostics'})
        return SchemaAnalysis(**data, contract_version=1, analysis_profile=profile,
                              supported=not any(d.severity == 'error' for d in diagnostics),
                              diagnostics=diagnostics)


def valid_default_value(expression, column_type):
    if expression.op == 'cast':
        literal = expression.args[0]
        value = convert_literal(literal.literal_value, literal.literal_type, expression.target_type, explicit=True)
        if value is False:
            return False
        if value is None:
            return True
        literal_value, literal_type = value
    elif expression.op == 'literal':
        literal_value, literal_type = expression.literal_value, expression.literal_type
    else:
        return True
    return convert_literal(literal_value, literal_type, column_type, explicit=False) is not False


def convert_literal(value, kind, target, explicit):
    if kind == 'null':
        return None
    name = target.name
    if name in {'smallint', 'integer', 'bigint', 'numeric'} and kind in {'integer', 'numeric', 'string'}:
        try:
            number = Decimal(value.strip())
            if not number.is_finite():
                if name == 'numeric' and (number.is_nan() or target.precision is None):
                    return value, 'numeric'
                return False
            if name in {'smallint', 'integer', 'bigint'}:
                # String literals use integer input syntax; numeric casts round half away from zero.
                if kind == 'string' and not re.fullmatch(r'[+-]?\d+', value.strip()):
                    return False
                number = number.to_integral_value(rounding=ROUND_HALF_UP)
                bits = {'smallint': 16, 'integer': 32, 'bigint': 64}[name]
                if not -(2 ** (bits - 1)) <= number < 2 ** (bits - 1):
                    return False
                return str(number), 'integer'
            if target.precision is not None:
                scale = target.scale or 0
                limit = Decimal(10) ** (target.precision - scale)
                if abs(number) >= limit:
                    return False
                with localcontext() as context:
                    context.prec = target.precision + abs(scale) + 4
                    number = number.quantize(Decimal(1).scaleb(-scale), rounding=ROUND_HALF_UP)
                if abs(number) >= limit:
                    return False
            return str(number), 'numeric'
        except (InvalidOperation, ValueError, OverflowError):
            return False
    if name == 'uuid' and kind == 'string':
        text = value.strip()
        if text.startswith('{') and text.endswith('}'):
            text = text[1:-1]
        parts = text.split('-')
        if (not all(parts) or any(len(part) % 4 for part in parts[:-1])
                or not re.fullmatch('[0-9a-fA-F]{32}', ''.join(parts))):
            return False
        return value, 'uuid'
    if name in {'varchar', 'text'} and kind == 'string':
        if name == 'varchar' and target.length is not None and len(value) > target.length:
            if explicit:
                value = value[:target.length]
            elif value[target.length:].strip(' '):
                return False
        return value, 'string'
    return value, kind
