import os
import shutil
import socket
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import text

from application_api.bootstrap import create_app
from application_api.config import Settings, require_capabilities
from application_api.database import Database, MIGRATION_LOCK_KEY, MIGRATIONS

pytestmark = pytest.mark.skipif(os.getenv("RUN_DATABASE_TESTS") != "1", reason="wymaga izolowanego Docker PostgreSQL")
PASSWORD = "test:@/%$' secret"


def docker(*args):
    return subprocess.run(["docker", *args], check=True, capture_output=True, text=True)


@pytest.fixture(scope="module")
def postgres():
    name = "s1t4-" + uuid.uuid4().hex[:12]
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    docker("run", "-d", "--name", name, "-p", f"127.0.0.1:{port}:5432", "-e", "POSTGRES_PASSWORD=admin-test", "-e", "POSTGRES_DB=testdb", "postgres:18.7-bookworm")
    try:
        for _ in range(100):
            if subprocess.run(["docker", "exec", name, "pg_isready", "-h", "127.0.0.1", "-U", "postgres", "-d", "testdb"], capture_output=True).returncode == 0:
                break
            time.sleep(.2)
        else:
            pytest.fail("PostgreSQL nie wystartował")
        sql = "CREATE ROLE app_user LOGIN PASSWORD 'test:@/%$'' secret' NOSUPERUSER NOCREATEDB NOCREATEROLE; CREATE SCHEMA app AUTHORIZATION app_user;"
        docker("exec", name, "psql", "-U", "postgres", "-d", "testdb", "-v", "ON_ERROR_STOP=1", "-c", sql)
        yield name, port
    finally:
        docker("rm", "-f", name)


@pytest.fixture
def db(postgres, tmp_path):
    _, port = postgres
    migrations = tmp_path / "migrations"
    shutil.copytree(MIGRATIONS, migrations, ignore=shutil.ignore_patterns("__pycache__"))
    settings = Settings(_env_file=None, app_db_host="127.0.0.1", app_db_port=str(port), app_db_name="testdb", app_db_user="app_user", app_db_password=PASSWORD)
    database = Database(settings, {"blocked_capabilities": []}, migrations)
    docker("exec", postgres[0], "psql", "-U", "postgres", "-d", "testdb", "-v", "ON_ERROR_STOP=1", "-c", "DROP SCHEMA app CASCADE; CREATE SCHEMA app AUTHORIZATION app_user")
    yield database
    database.close()


def test_start_restart_health_and_guard(db):
    db.start()
    assert db.report()["status"] == "ready"
    db.start()
    assert db.report()["migration_status"] == "applied"
    with db.session() as session:
        assert session.execute(text("SELECT current_schema()" )).scalar_one() == "app"
        assert session.execute(text("SELECT count(*) FROM app.alembic_version")).scalar_one() == 1
    app = create_app()
    app.state.config_report = {"blocked_capabilities": []}
    app.state.database = db
    @app.get("/guarded", dependencies=[Depends(require_capabilities("database"))])
    def guarded():
        return {"ok": True}
    client = TestClient(app)
    assert client.get("/guarded").status_code == 200
    with db.engine.begin() as conn:
        conn.execute(text("DELETE FROM app.alembic_version"))
    assert client.get("/health/database").json()["issues"][0]["code"] == "schema_version_missing"
    assert client.get("/guarded").status_code == 503
    assert client.get("/health/database").json()["status"] == "unavailable"


def test_failed_migration_rolls_back_and_does_not_retry(db):
    revision = db.migrations / "versions" / "0002_test.py"
    revision.write_text('from alembic import op\nrevision="0002_test"\ndown_revision="0001_initial"\nbranch_labels=None\ndepends_on=None\ndef upgrade():\n op.execute("CREATE TABLE app.test_only (id int)")\n op.execute("SELECT 1/0")\n')
    db.start()
    assert db.report()["issues"][0]["code"] == "migration_failed"
    with db.engine.connect() as conn:
        assert conn.execute(text("SELECT to_regclass('app.test_only')")).scalar_one() is None
        assert conn.execute(text("SELECT to_regclass('app.alembic_version')")).scalar_one() is None
    revision.write_text(revision.read_text().replace(' op.execute("SELECT 1/0")\n', ''))
    assert db.report()["migration_status"] == "failed"
    db.start()
    assert db.report()["status"] == "unavailable"
    shutil.rmtree(db.migrations / "versions" / "__pycache__", ignore_errors=True)
    restarted = Database(None, {"blocked_capabilities": []})
    restarted.engine, restarted.migrations, restarted.startup_issue = db.engine, db.migrations, None
    restarted.start()
    assert restarted.report()["status"] == "ready"


def test_parallel_and_lock_timeout(db):
    with ThreadPoolExecutor(max_workers=2) as pool:
        others = [Database(None, {"blocked_capabilities": []}) for _ in range(2)]
        for other in others:
            other.engine = db.engine
            other.migrations = db.migrations
            other.startup_issue = None
        list(pool.map(lambda d: d.start(), others))
    assert all(d.report()["status"] == "ready" for d in others)
    with db.engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": MIGRATION_LOCK_KEY})
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(db.start).result(timeout=10)
    assert db.report()["issues"][0]["code"] == "lock_timeout"


def test_connection_credentials_and_recovery(db, postgres, caplog):
    db.start()
    name, _ = postgres
    docker("stop", name)
    assert db.report()["issues"][0]["code"] == "connection_failed"
    docker("start", name)
    for _ in range(100):
        if db.report()["status"] == "ready":
            break
        time.sleep(.2)
    assert db.report()["status"] == "ready"
    bad = Database(Settings(_env_file=None, app_db_host="127.0.0.1", app_db_port=str(postgres[1]), app_db_name="testdb", app_db_user="app_user", app_db_password=PASSWORD + "bad"), {"blocked_capabilities": []})
    bad.start()
    assert bad.report()["issues"][0]["code"] == "connection_failed"
    assert PASSWORD not in str(bad.report()) + caplog.text
    bad.close()


def test_admin_rejected(postgres):
    db = Database(Settings(_env_file=None, app_db_host="127.0.0.1", app_db_port=str(postgres[1]), app_db_name="testdb", app_db_user="postgres", app_db_password="admin-test"), {"blocked_capabilities": []})
    db.start()
    assert db.report()["issues"][0]["code"] == "invalid_privileges"
    db.close()


def test_concurrent_processes(db, postgres):
    script = '''from application_api.config import Settings
from application_api.database import Database
import sys
settings = Settings(_env_file=None, app_db_host="127.0.0.1", app_db_port=sys.argv[1], app_db_name="testdb", app_db_user="app_user", app_db_password="test:@/%$\\' secret")
db = Database(settings, {"blocked_capabilities": []}, sys.argv[2])
db.start()
assert db.report()["status"] == "ready", db.report()
db.close()
'''
    processes = [subprocess.Popen([os.sys.executable, "-c", script, str(postgres[1]), str(db.migrations)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
    for process in processes:
        _, stderr = process.communicate(timeout=20)
        assert process.returncode == 0, stderr
    db.start()
    assert db.report()["status"] == "ready"


def test_provisioning(postgres):
    name = "s1t4-init-" + uuid.uuid4().hex[:12]
    root = Path(__file__).resolve().parents[3]
    image = "s1t4-init:" + uuid.uuid4().hex[:12]
    docker("build", "-t", image, "-f", str(root / "docker/postgres/Dockerfile"), str(root))
    docker("run", "-d", "--name", name, "-e", "POSTGRES_PASSWORD=admin-test", "-e", "POSTGRES_DB=testdb", "-e", "APP_DB_USER=app_user", "-e", "APP_DB_PASSWORD=" + PASSWORD, image)
    try:
        for _ in range(100):
            # Environment must be passed to the container, not only to docker's client.
            result = subprocess.run(["docker", "exec", "-e", "PGPASSWORD=" + PASSWORD, name, "psql", "-h", "127.0.0.1", "-U", "app_user", "-d", "testdb", "-c", "SELECT current_user"], capture_output=True, text=True)
            if result.returncode == 0:
                break
            time.sleep(.2)
        assert result.returncode == 0, result.stderr
        result = docker("exec", name, "psql", "-U", "postgres", "-d", "testdb", "-Atc", "SELECT rolname, rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname='app_user'; SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname='app'")
        assert "app_user|f|f|f" in result.stdout
        assert result.stdout.splitlines()[-1] == "app_user"
    finally:
        docker("rm", "-f", name)
        docker("image", "rm", image)


def test_missing_configuration_and_unreachable_server():
    missing = Database(None, {"blocked_capabilities": ["database"]})
    missing.start()
    assert missing.report()["migration_status"] == "not_run"
    assert missing.report()["issues"][0]["code"] == "configuration_missing"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    settings = Settings(_env_file=None, app_db_host="127.0.0.1", app_db_port=str(port), app_db_name="testdb", app_db_user="app_user", app_db_password=PASSWORD)
    unreachable = Database(settings, {"blocked_capabilities": []})
    unreachable.start()
    assert unreachable.report()["issues"][0]["code"] == "connection_failed"
    unreachable.close()


def test_session_commit_and_rollback(db):
    db.start()
    with db.session() as session:
        session.execute(text("CREATE TABLE app.session_test (id integer)"))
        session.execute(text("INSERT INTO app.session_test VALUES (1)"))
    with pytest.raises(RuntimeError), db.session() as session:
        session.execute(text("INSERT INTO app.session_test VALUES (2)"))
        raise RuntimeError("test")
    with db.session() as session:
        assert session.execute(text("SELECT id FROM app.session_test")).scalars().all() == [1]
