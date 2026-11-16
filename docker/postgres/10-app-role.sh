#!/bin/sh
set -eu
if [ -z "${APP_DB_USER:-}" ] && [ -z "${APP_DB_PASSWORD:-}" ]; then
    exit 0
fi
if [ -z "${APP_DB_USER:-}" ] || [ -z "${APP_DB_PASSWORD:-}" ] || [ "$APP_DB_USER" = "$POSTGRES_USER" ]; then
    echo 'Invalid application database role configuration' >&2
    exit 1
fi
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv app_user APP_DB_USER
\getenv app_password APP_DB_PASSWORD
\getenv db_name POSTGRES_DB
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE', :'app_user', :'app_password')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'app_user') \gexec
SELECT format('GRANT CONNECT ON DATABASE %I TO %I', :'db_name', :'app_user') \gexec
SELECT format('CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION %I', :'app_user') \gexec
SQL
