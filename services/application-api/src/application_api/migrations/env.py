from alembic import context

connection = context.config.attributes["connection"]
context.configure(connection=connection, version_table_schema="app", transactional_ddl=True)
with context.begin_transaction():
    context.run_migrations()
