"""Short-lived database operations and startup-only schema migrations."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# Shared by every application-api instance, including future deployments.
MIGRATION_LOCK_KEY = 1395733556
MIGRATIONS = Path(__file__).parent / "migrations"
MESSAGES = {
    "configuration_missing": "Brak poprawnej konfiguracji bazy.",
    "connection_failed": "Nie można połączyć się z bazą.",
    "invalid_privileges": "Konto lub schemat bazy ma niewłaściwe uprawnienia.",
    "lock_timeout": "Przekroczono czas oczekiwania na blokadę migracji.",
    "migration_failed": "Nie udało się zastosować migracji bazy.",
    "schema_version_missing": "Brak wymaganej wersji schematu bazy.",
}


class InvalidPrivileges(Exception):
    pass


def migration_config(path=MIGRATIONS):
    config = Config()
    config.set_main_option("script_location", str(path))
    return config


class Database:
    def __init__(self, settings, config_report, migrations=MIGRATIONS):
        self.engine = None
        self._started = False
        self.migrations = migrations
        self.migration_status = "not_run"
        self.startup_issue = None
        if settings is None or "database" in config_report["blocked_capabilities"]:
            self.startup_issue = "configuration_missing"
            return
        url = URL.create("postgresql+psycopg", username=settings.app_db_user,
                         password=settings.app_db_password.get_secret_value(),
                         host=settings.app_db_host, port=settings.app_db_port,
                         database=settings.app_db_name)
        self.engine = create_engine(url, pool_size=5, max_overflow=0, pool_timeout=3,
                                    pool_pre_ping=True, connect_args={"connect_timeout": 3,
                                    "options": "-csearch_path=app -cstatement_timeout=15000"})
        self.sessions = sessionmaker(self.engine)

    @contextmanager
    def session(self):
        with self.sessions() as session:
            with session.begin():
                yield session

    def start(self):
        if self._started:
            return
        self._started = True
        if self.engine is None:
            return
        try:
            with self.engine.begin() as connection:
                role_ok = connection.execute(text("""SELECT NOT (rolsuper OR rolcreatedb OR rolcreaterole)
                    FROM pg_roles WHERE rolname = current_user""")).scalar_one()
                schema_ok = connection.execute(text("""SELECT EXISTS (SELECT 1 FROM pg_namespace
                    WHERE nspname = 'app' AND pg_get_userbyid(nspowner) = current_user
                    AND has_schema_privilege(current_user, oid, 'USAGE, CREATE'))""")).scalar_one()
                if not role_ok or not schema_ok:
                    raise InvalidPrivileges
                connection.execute(text("SET LOCAL lock_timeout = '5s'"))
                connection.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": MIGRATION_LOCK_KEY})
                config = migration_config(self.migrations)
                config.attributes["connection"] = connection
                command.upgrade(config, "head")
            self.migration_status = "applied"
        except InvalidPrivileges:
            self.migration_status, self.startup_issue = "failed", "invalid_privileges"
        except Exception as exc:
            self.migration_status = "failed"
            if isinstance(exc, DBAPIError) and getattr(exc.orig, "sqlstate", None) == "55P03":
                self.startup_issue = "lock_timeout"
            elif isinstance(exc, SQLAlchemyError) and (getattr(exc, "connection_invalidated", False) or self._connection_error(exc)):
                self.startup_issue = "connection_failed"
            else:
                self.startup_issue = "migration_failed"

    @staticmethod
    def _connection_error(exc):
        state = getattr(getattr(exc, "orig", None), "sqlstate", None)
        return state is None or state.startswith("08") or state == "28P01"

    def report(self):
        issue = self.startup_issue
        if self.migration_status == "applied":
            try:
                with self.engine.connect() as connection:
                    versions = set(connection.execute(text("SELECT version_num FROM app.alembic_version")).scalars())
                if versions != set(ScriptDirectory.from_config(migration_config(self.migrations)).get_heads()):
                    issue = "schema_version_missing"
            except SQLAlchemyError as exc:
                issue = "connection_failed" if self._connection_error(exc) else "schema_version_missing"
        return {"service": "application-api", "dependency": "database",
                "status": "unavailable" if issue else "ready", "migration_status": self.migration_status,
                "issues": [{"code": issue, "message": MESSAGES[issue]}] if issue else [],
                "blocked_capabilities": ["database"] if issue else [],
                "checked_at": datetime.now(timezone.utc).isoformat()}

    def close(self):
        if self.engine is not None:
            self.engine.dispose()
