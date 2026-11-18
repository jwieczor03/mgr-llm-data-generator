import os
import shutil
import socket
import subprocess
import time
import uuid

import pytest
from application_api import bootstrap
from application_api.config import FIELDS, Settings
from application_api.database import MIGRATIONS, Database


@pytest.fixture(autouse=True)
def isolate_configuration(monkeypatch, tmp_path):
    for name in os.environ:
        if name.lower() in FIELDS:
            monkeypatch.delenv(name)
    original = bootstrap.load_config
    monkeypatch.setattr(bootstrap, "load_config", lambda: original(tmp_path / "missing.env"))


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
        docker("rm", "-fv", name)


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
