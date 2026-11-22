"""Parse PostgreSQL DDL into application-owned structures, without executing it."""
import hashlib
from bisect import bisect_left
from uuid import uuid5

from pglast import Error, ast, enums, parse_sql
from pglast.parser import scan

from application_api.schema_contracts import (
    Column,
    Constraint,
    Diagnostic,
    Expression,
    ParsedSchema,
    Relation,
    SourceLocation,
    SqlType,
    Table,
    manifest_digest,
)


class DdlParser:
    def __init__(self, read_file):
        self.read_file = read_file

    def parse(self, bundle, profile):
        if manifest_digest(bundle.files) != bundle.manifest_hash:
            raise ValueError('manifest hash mismatch')
        self.bundle = bundle
        self.tables, self.columns, self.constraints, self.relations, self.diagnostics = [], [], [], [], []
        self.table_by_name, self.columns_by_table = {}, {}
        self.schemas, self.search_path = {'public'}, ['public']
        self.sources = []
        pieces = []
        for index, file in enumerate(bundle.files):
            if file.position != index:
                raise ValueError('invalid manifest order')
            raw = self.read_file(file)
            if len(raw) != file.size_bytes or hashlib.sha256(raw).hexdigest() != file.sha256:
                raise ValueError('file differs from manifest')
            text = raw.decode('utf-8-sig')
            start = sum(len(piece) for piece in pieces)
            self.sources.append((start, start + len(text), file.file_id, text))
            pieces.extend((text, '\n'))
        self.sql = ''.join(pieces[:-1])
        try:
            self.tokens = scan(self.sql)
            self.token_starts = [token.start for token in self.tokens]
            statements = parse_sql(self.sql)
        except Error as error:
            offset = error.args[1] if len(error.args) > 1 else None
            self.diagnose('DDL_SYNTAX_ERROR', str(error.args[0]), offset)
            return self.result()
        for raw in statements:
            statement = raw.stmt
            self.statement_offset = raw.stmt_location
            self.statement_original = self.sql[raw.stmt_location:raw.stmt_location + raw.stmt_len] if raw.stmt_len else self.sql[raw.stmt_location:]
            if isinstance(statement, ast.CreateSchemaStmt):
                if statement.schemaname is None or statement.authrole is not None or statement.schemaElts:
                    self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported CREATE SCHEMA', raw.stmt_location)
                elif statement.schemaname in self.schemas and not statement.if_not_exists:
                    self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Duplicate schema', raw.stmt_location)
                else:
                    self.schemas.add(statement.schemaname)
            elif isinstance(statement, ast.VariableSetStmt) and statement.name == 'search_path' and statement.args and not statement.is_local:
                if all(isinstance(x, ast.A_Const) and isinstance(x.val, ast.String) for x in statement.args):
                    self.search_path = [x.val.sval for x in statement.args]
                else:
                    self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported search_path', raw.stmt_location)
            elif isinstance(statement, ast.CreateStmt):
                self.create_table(statement)
            elif isinstance(statement, ast.AlterTableStmt):
                self.alter_table(statement)
            else:
                self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported statement', raw.stmt_location)
        return self.result()

    def result(self):
        return ParsedSchema(schema_version_id=self.bundle.schema_version_id, tables=self.tables,
                            columns=self.columns, constraints=self.constraints, relations=self.relations,
                            diagnostics=self.diagnostics)

    def location(self, offset):
        if offset is None or offset < 0:
            return None
        for start, end, file_id, text in self.sources:
            if start <= offset < end:
                prefix = text[:offset - start]
                return SourceLocation(file_id=file_id, line=prefix.count('\n') + 1,
                                      column=len(prefix.rsplit('\n', 1)[-1]) + 1)
        return None

    def diagnose(self, code, message, offset=None, object_ids=()):
        self.diagnostics.append(Diagnostic(code=code, message=message, severity='error',
                                           scope='object' if object_ids else 'bundle',
                                           object_ids=list(object_ids), location=self.location(offset)))

    def original_identifier(self, offset, qualified=False):
        if offset is None or offset < 0:
            return ''
        index = bisect_left(self.token_starts, offset)
        if index >= len(self.tokens) or self.tokens[index].start != offset:
            return ''
        token = self.tokens[index]
        if qualified and index + 2 < len(self.tokens) and self.tokens[index + 1].name == 'ASCII_46':
            token = self.tokens[index + 2]
        return self.sql[token.start:token.end + 1]

    def identity(self, kind, *parts):
        return uuid5(self.bundle.schema_version_id, ':'.join(map(str, (kind, *parts))))

    def resolve(self, relation):
        if relation.schemaname:
            return self.table_by_name.get((relation.schemaname, relation.relname))
        return next((self.table_by_name[(s, relation.relname)] for s in self.search_path
                     if (s, relation.relname) in self.table_by_name), None)

    def type_of(self, node):
        if len(node.names) > 1 and [part.sval for part in node.names[:-1]] != ['pg_catalog']:
            return None
        name = node.names[-1].sval
        aliases = {'int2': 'smallint', 'int4': 'integer', 'int8': 'bigint', 'bool': 'boolean',
                   'serial': 'integer', 'bigserial': 'bigint'}
        name = aliases.get(name, name)
        if name not in {'smallint', 'integer', 'bigint', 'numeric', 'text', 'varchar',
                        'boolean', 'uuid', 'date', 'timestamp', 'timestamptz'} or node.arrayBounds or node.setof or node.pct_type:
            return None
        params = [p.val.ival for p in node.typmods or () if isinstance(p, ast.A_Const) and isinstance(p.val, ast.Integer)]
        if node.typmods and len(params) != len(node.typmods):
            return None
        if params and params[0] < 0:
            return None
        if name == 'varchar' and len(params) == 1:
            return SqlType(name=name, length=params[0])
        if name == 'numeric' and 1 <= len(params) <= 2:
            return SqlType(name=name, precision=params[0], scale=params[1] if len(params) == 2 else 0)
        if params:
            return None
        return SqlType(name=name)

    def create_table(self, node):
        if (node.relation.relpersistence != 'p' or node.inhRelations or node.partspec or node.ofTypename
                or node.constraints or node.options or node.accessMethod or node.tablespacename
                or node.if_not_exists or node.oncommit != enums.OnCommitAction.ONCOMMIT_NOOP):
            self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported CREATE TABLE option', self.statement_offset)
            return
        schema = node.relation.schemaname or next((s for s in self.search_path if s in self.schemas), None)
        key = (schema, node.relation.relname)
        if schema not in self.schemas or key in self.table_by_name:
            self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Missing schema or duplicate table', node.relation.location)
            return
        table = Table(table_id=self.identity('table', len(self.tables)), schema_name=schema,
                      name=node.relation.relname, original_name=self.original_identifier(node.relation.location, qualified=True),
                      location=self.location(node.relation.location))
        self.tables.append(table)
        self.table_by_name[key] = table
        self.columns_by_table[table.table_id] = {}
        for element in node.tableElts or ():
            if not isinstance(element, ast.ColumnDef):
                continue
            if element.colname in self.columns_by_table[table.table_id]:
                self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Duplicate column', element.location, [table.table_id])
                continue
            if element.collClause or element.compression or element.fdwoptions or element.storage_name:
                self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported column option', element.location, [table.table_id])
            sql_type = self.type_of(element.typeName)
            if sql_type is None:
                self.diagnose('DDL_UNSUPPORTED_TYPE', 'Unsupported column type', element.location, [table.table_id])
                continue
            kind = element.typeName.names[-1].sval
            auto = kind if kind in {'serial', 'bigserial'} else None
            col = Column(column_id=self.identity('column', table.table_id, len(self.columns_by_table[table.table_id])),
                         table_id=table.table_id, position=len(self.columns_by_table[table.table_id]), name=element.colname,
                         original_name=self.original_identifier(element.location), type=sql_type, nullable=auto is None,
                         automatic_id=auto, location=self.location(element.location))
            self.columns.append(col)
            self.columns_by_table[table.table_id][col.name] = col
        pending_foreign_keys = []
        for element in node.tableElts or ():
            if isinstance(element, ast.ColumnDef):
                column = self.columns_by_table[table.table_id].get(element.colname)
                if column:
                    self.column_constraints(table, column, element.constraints or (), pending_foreign_keys)
            elif isinstance(element, ast.Constraint):
                if element.contype == enums.ConstrType.CONSTR_FOREIGN:
                    pending_foreign_keys.append((element, None))
                else:
                    self.add_constraint(table, element)
            else:
                self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported table element', self.statement_offset, [table.table_id])
        for foreign_key, column in pending_foreign_keys:
            self.add_constraint(table, foreign_key, column)

    def update_column(self, column, **changes):
        updated = column.model_copy(update=changes)
        self.columns[self.columns.index(column)] = updated
        self.columns_by_table[column.table_id][column.name] = updated
        return updated

    def column_constraints(self, table, column, constraints, pending_foreign_keys):
        seen_default = False
        seen_identity = False
        for index, item in enumerate(constraints):
            kind = item.contype
            if kind in {enums.ConstrType.CONSTR_FOREIGN, enums.ConstrType.CONSTR_PRIMARY, enums.ConstrType.CONSTR_UNIQUE}:
                attributes = []
                for following in constraints[index + 1:]:
                    if following.contype not in {enums.ConstrType.CONSTR_ATTR_DEFERRABLE,
                                                 enums.ConstrType.CONSTR_ATTR_NOT_DEFERRABLE,
                                                 enums.ConstrType.CONSTR_ATTR_DEFERRED,
                                                 enums.ConstrType.CONSTR_ATTR_IMMEDIATE}:
                        break
                    attributes.append(following.contype)
                item.initdeferred = enums.ConstrType.CONSTR_ATTR_DEFERRED in attributes
                explicit_not_deferrable = enums.ConstrType.CONSTR_ATTR_NOT_DEFERRABLE in attributes
                if item.initdeferred and explicit_not_deferrable:
                    self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Conflicting constraint deferral', item.location, [column.column_id])
                item.deferrable = (enums.ConstrType.CONSTR_ATTR_DEFERRABLE in attributes or
                                   (item.initdeferred and not explicit_not_deferrable))
            if kind == enums.ConstrType.CONSTR_NOTNULL:
                column = self.update_column(column, nullable=False)
            elif kind == enums.ConstrType.CONSTR_NULL:
                column = self.update_column(column, nullable=True)
            elif kind == enums.ConstrType.CONSTR_DEFAULT:
                if seen_default:
                    self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Duplicate DEFAULT', item.location, [column.column_id])
                    continue
                seen_default = True
                expression = self.expression(item.raw_expr, table, item)
                if not self.valid_default(expression):
                    self.diagnose('DDL_UNSUPPORTED_EXPRESSION', 'Unsupported or incompatible DEFAULT', item.location, [column.column_id])
                    expression = expression.model_copy(update={'op': 'unsupported', 'original': self.statement_original,
                                                               'original_scope': 'statement'})
                column = self.update_column(column, default=expression)
            elif kind == enums.ConstrType.CONSTR_IDENTITY:
                if seen_identity:
                    self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Duplicate IDENTITY', item.location, [column.column_id])
                    continue
                seen_identity = True
                if item.options:
                    self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported IDENTITY options', item.location, [column.column_id])
                column = self.update_column(column, automatic_id='identity_always' if item.generated_when == 'a' else 'identity_by_default', nullable=False)
            elif kind == enums.ConstrType.CONSTR_FOREIGN:
                pending_foreign_keys.append((item, column))
            elif kind in {enums.ConstrType.CONSTR_PRIMARY, enums.ConstrType.CONSTR_UNIQUE,
                          enums.ConstrType.CONSTR_CHECK}:
                self.add_constraint(table, item, column)
            elif kind not in {enums.ConstrType.CONSTR_ATTR_DEFERRABLE, enums.ConstrType.CONSTR_ATTR_NOT_DEFERRABLE,
                              enums.ConstrType.CONSTR_ATTR_DEFERRED, enums.ConstrType.CONSTR_ATTR_IMMEDIATE}:
                self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported column constraint', item.location, [column.column_id])

    def valid_check(self, expression):
        if expression.op in {'current_date', 'current_timestamp', 'unsupported'}:
            return False
        if expression.op == 'cast' and (len(expression.args) != 1 or expression.args[0].op != 'literal'):
            return False
        return all(self.valid_check(argument) for argument in expression.args)

    def valid_default(self, expression):
        if expression.op in {'unsupported', 'literal', 'current_date', 'current_timestamp'}:
            return True  # Unsupported conversion already produced a diagnostic.
        return (expression.op == 'cast' and len(expression.args) == 1
                and expression.args[0].op == 'literal')

    def original_expression(self, constraint):
        # Scanner tokens preserve literals and comments without interpreting SQL.
        if constraint.location < 0:
            return self.statement_original, 'statement'
        start = bisect_left(self.token_starts, constraint.location)
        tokens = (self.tokens[index] for index in range(start, len(self.tokens)))
        first = next(tokens, None)
        if first is None:
            return self.statement_original, 'statement'
        if first.name == 'CONSTRAINT':
            next(tokens, None)  # constraint name
            first = next(tokens, None)
        if first is None:
            return self.statement_original, 'statement'
        if constraint.contype == enums.ConstrType.CONSTR_CHECK and first.name == 'CHECK':
            opening = next(tokens, None)
            if opening and opening.name == 'ASCII_40':
                depth = 1
                for token in tokens:
                    if token.name == 'ASCII_40':
                        depth += 1
                    elif token.name == 'ASCII_41':
                        depth -= 1
                        if depth == 0:
                            return self.sql[opening.end + 1:token.start], 'expression'
        if constraint.contype == enums.ConstrType.CONSTR_DEFAULT and first.name == 'DEFAULT':
            opening = next(tokens, None)
            if opening is None:
                return self.statement_original, 'statement'
            depth = 1 if opening.name == 'ASCII_40' else 0
            boundary = {'CONSTRAINT', 'CHECK', 'NOT', 'NULL_P', 'UNIQUE', 'PRIMARY',
                        'REFERENCES', 'GENERATED', 'COLLATE', 'ASCII_44', 'ASCII_41', 'ASCII_59'}
            for token in tokens:
                if depth == 0 and token.name in boundary:
                    return self.sql[opening.start:token.start].rstrip(), 'expression'
                if token.name == 'ASCII_40':
                    depth += 1
                elif token.name == 'ASCII_41':
                    depth -= 1
        return self.statement_original, 'statement'

    def expression(self, node, table, constraint):
        try:
            expr = self.convert_expression(node, table)
            if constraint.contype == enums.ConstrType.CONSTR_CHECK and not self.valid_check(expr):
                raise ValueError('unsupported CHECK')
        except (ValueError, TypeError, AttributeError):
            self.diagnose('DDL_UNSUPPORTED_EXPRESSION', 'Unsupported expression', getattr(node, 'location', None), [table.table_id])
            expr = Expression(op='unsupported')
        if constraint.contype == enums.ConstrType.CONSTR_DEFAULT and expr.op == 'unsupported':
            original, scope = self.statement_original, 'statement'
        else:
            original, scope = self.original_expression(constraint)
        return expr.model_copy(update={'original': original, 'original_scope': scope})

    def convert_expression(self, node, table):
        if isinstance(node, ast.A_Const):
            if node.isnull:
                return Expression(op='literal', literal_type='null', literal_value='null')
            value = node.val
            if isinstance(value, ast.Integer):
                return Expression(op='literal', literal_type='integer', literal_value=str(value.ival))
            if isinstance(value, ast.Float):
                return Expression(op='literal', literal_type='integer' if value.fval.lstrip('+-').isdigit() else 'numeric', literal_value=value.fval)
            if isinstance(value, ast.String):
                return Expression(op='literal', literal_type='string', literal_value=value.sval)
            if isinstance(value, ast.Boolean):
                return Expression(op='literal', literal_type='boolean', literal_value=str(value.boolval).lower())
        if isinstance(node, ast.ColumnRef) and all(isinstance(field, ast.String) for field in node.fields):
            parts = [field.sval for field in node.fields]
            if len(parts) == 1:
                name = parts[0]
            elif len(parts) == 2 and parts[0] == table.name:
                name = parts[1]
            elif len(parts) == 3 and parts[:2] == [table.schema_name, table.name]:
                name = parts[2]
            else:
                raise ValueError('unsupported column qualifier')
            column = self.columns_by_table[table.table_id].get(name)
            if not column:
                self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Unknown column in expression', node.location, [table.table_id])
                raise ValueError('unknown column')
            return Expression(op='column', column_id=column.column_id)
        if isinstance(node, ast.TypeCast):
            sql_type = self.type_of(node.typeName)
            if sql_type is None:
                raise ValueError('unsupported cast')
            return Expression(op='cast', args=[self.convert_expression(node.arg, table)], target_type=sql_type)
        if isinstance(node, ast.SQLValueFunction):
            mapping = {enums.SQLValueFunctionOp.SVFOP_CURRENT_DATE: 'current_date',
                       enums.SQLValueFunctionOp.SVFOP_CURRENT_TIMESTAMP: 'current_timestamp'}
            if node.op in mapping:
                return Expression(op=mapping[node.op])
        if isinstance(node, ast.BoolExpr):
            op = {enums.BoolExprType.AND_EXPR: 'and', enums.BoolExprType.OR_EXPR: 'or',
                  enums.BoolExprType.NOT_EXPR: 'not'}.get(node.boolop)
            if op:
                return Expression(op=op, args=[self.convert_expression(x, table) for x in node.args])
        if isinstance(node, ast.A_Expr):
            kind = node.kind
            if kind == enums.A_Expr_Kind.AEXPR_OP:
                op = node.name[0].sval
                if op not in {'=', '<>', '!=', '<', '<=', '>', '>='} or node.lexpr is None:
                    raise ValueError('unsupported operator')
                return Expression(op=op, args=[self.convert_expression(node.lexpr, table), self.convert_expression(node.rexpr, table)])
            if kind in {enums.A_Expr_Kind.AEXPR_BETWEEN, enums.A_Expr_Kind.AEXPR_NOT_BETWEEN,
                         enums.A_Expr_Kind.AEXPR_IN}:
                op = 'in' if kind == enums.A_Expr_Kind.AEXPR_IN else 'between'
                result = Expression(op=op, args=[self.convert_expression(node.lexpr, table)] +
                                    [self.convert_expression(x, table) for x in node.rexpr])
                negated = kind == enums.A_Expr_Kind.AEXPR_NOT_BETWEEN or (op == 'in' and node.name[0].sval == '<>')
                return Expression(op='not', args=[result]) if negated else result
        raise ValueError('unsupported expression')

    def add_constraint(self, table, item, column=None):
        kinds = {enums.ConstrType.CONSTR_PRIMARY: 'primary_key', enums.ConstrType.CONSTR_UNIQUE: 'unique',
                 enums.ConstrType.CONSTR_FOREIGN: 'foreign_key', enums.ConstrType.CONSTR_CHECK: 'check'}
        kind = kinds.get(item.contype)
        if not kind:
            self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported constraint', item.location, [table.table_id])
            return
        if (item.skip_validation or item.is_no_inherit or item.nulls_not_distinct or item.including or item.options
                or item.indexname or item.indexspace or item.without_overlaps
                or (kind == 'check' and (item.deferrable or item.initdeferred or not item.is_enforced))):
            self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported constraint option', item.location, [table.table_id])
            return
        source_names = ([column.name] if column else [x.sval for x in (item.fk_attrs if kind == 'foreign_key' else item.keys) or ()])
        columns = self.columns_by_table[table.table_id]
        if any(name not in columns for name in source_names):
            self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Unknown constraint column', item.location, [table.table_id])
            return
        if item.conname and any(c.table_id == table.table_id and c.name == item.conname for c in self.constraints):
            self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Duplicate constraint name', item.location, [table.table_id])
            return
        cid = self.identity('constraint', table.table_id, len(self.constraints))
        expression = self.expression(item.raw_expr, table, item) if kind == 'check' else None
        check_columns = []
        def collect_columns(expr):
            if expr.column_id is not None and expr.column_id not in check_columns:
                check_columns.append(expr.column_id)
            for arg in expr.args:
                collect_columns(arg)
        if expression is not None:
            collect_columns(expression)
        c = Constraint(constraint_id=cid, table_id=table.table_id, kind=kind,
                       column_ids=check_columns if kind == 'check' else [columns[name].column_id for name in source_names], name=item.conname,
                       expression=expression, deferrable=item.deferrable, initially_deferred=item.initdeferred,
                       location=self.location(item.location))
        if kind == 'foreign_key':
            if item.fk_del_set_cols or item.skip_validation or not item.is_enforced:
                self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported foreign key option', item.location, [table.table_id])
                return
            target = self.resolve(item.pktable)
            if target is None:
                self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Unknown referenced table', item.location, [table.table_id])
                return
            target_columns = self.columns_by_table[target.table_id]
            target_names = [x.sval for x in item.pk_attrs or ()]
            if not target_names:
                primary = next((x for x in self.constraints if x.table_id == target.table_id and x.kind == 'primary_key'), None)
                target_ids = primary.column_ids if primary else []
            else:
                if len(target_names) != len(source_names) or any(name not in target_columns for name in target_names):
                    self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Unknown referenced columns', item.location, [table.table_id, target.table_id])
                    return
                target_ids = [target_columns[name].column_id for name in target_names]
            if len(target_ids) != len(source_names) or not target_ids:
                self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Unknown referenced columns', item.location, [table.table_id, target.table_id])
                return
            actions = {'a': 'no_action', 'r': 'restrict', 'c': 'cascade', 'n': 'set_null', 'd': 'set_default'}
            match = {'s': 'simple', 'f': 'full'}.get(item.fk_matchtype)
            if match is None or item.fk_upd_action not in actions or item.fk_del_action not in actions:
                self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported foreign key attributes', item.location, [table.table_id])
                return
            self.relations.append(Relation(constraint_id=cid, source_table_id=table.table_id,
                                           target_table_id=target.table_id, column_pairs=list(zip(c.column_ids, target_ids)),
                                           match=match, on_update=actions[item.fk_upd_action], on_delete=actions[item.fk_del_action],
                                           deferrable=c.deferrable, initially_deferred=c.initially_deferred))
        self.constraints.append(c)
        if kind == 'primary_key':
            for name in source_names:
                self.update_column(columns[name], nullable=False)

    def alter_table(self, node):
        if node.objtype != enums.ObjectType.OBJECT_TABLE:
            self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported ALTER object type', self.statement_offset)
            return
        table = self.resolve(node.relation)
        if table is None:
            self.diagnose('DDL_UNRESOLVED_REFERENCE', 'Unknown ALTER TABLE target', node.relation.location)
            return
        for command in node.cmds:
            if command.subtype == enums.AlterTableType.AT_AddConstraint and isinstance(command.def_, ast.Constraint):
                self.add_constraint(table, command.def_)
            else:
                self.diagnose('DDL_UNSUPPORTED_STATEMENT', 'Unsupported ALTER TABLE action', self.statement_offset, [table.table_id])
