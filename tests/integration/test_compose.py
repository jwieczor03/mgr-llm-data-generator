"""Opt-in tests of real containers, using a disposable Compose project and database."""

import json
import os
from pathlib import Path
import re
import secrets
import subprocess
from urllib.request import urlopen
from uuid import uuid4

import pytest


ROOT = Path(__file__).resolve().parents[2]
BACKENDS = ("application-api", "generation-service", "validation-service")
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_COMPOSE_TESTS") != "1",
    reason="Set RUN_COMPOSE_TESTS=1 to build and test an isolated Docker Compose environment.",
)


class Stack:
    def __init__(self, directory: Path):
        self.directory = directory
        self.command = [
            "docker", "compose", "--project-name", f"s1-t3-test-{uuid4().hex[:12]}",
            "--project-directory", str(ROOT), "--env-file", str(directory / "database.env"),
            "-f", str(ROOT / "compose.yaml"), "-f", str(directory / "override.yaml"),
        ]
        # Host configuration must not change the test's credentials or project selection.
        self.environment = {
            key: value for key, value in os.environ.items()
            if not key.startswith(("COMPOSE_", "POSTGRES_"))
        }

    def run(self, *arguments: str, input: str | None = None) -> str:
        result = subprocess.run(
            [*self.command, *arguments], input=input, capture_output=True,
            text=True, check=True, timeout=300, env=self.environment,
        )
        return result.stdout.strip()

    def get(self, path: str) -> tuple[int, str, str]:
        address = self.run("port", "application-api", "8000")
        with urlopen(f"http://{address}{path}", timeout=5) as response:
            return response.status, response.headers.get_content_type(), response.read().decode()

    def sql(self, statement: str) -> str:
        return self.run(
            "exec", "-T", "app-db", "psql", "-U", "compose_test", "-d", "compose_test",
            "-v", "ON_ERROR_STOP=1", "-At", input=statement,
        )


@pytest.fixture(scope="module")
def stack(tmp_path_factory):
    directory = tmp_path_factory.mktemp("compose")
    password = secrets.token_hex(24)
    (directory / "database.env").write_text(
        f"POSTGRES_DB=compose_test\nPOSTGRES_USER=compose_test\nPOSTGRES_PASSWORD={password}\n"
    )
    (directory / "application-api.env").write_text(
        "APP_DB_HOST=app-db\nAPP_DB_PORT=5432\nAPP_DB_NAME=compose_test\n"
        f"APP_DB_USER=compose_test\nAPP_DB_PASSWORD={password}\n"
        "GENERATION_SERVICE_URL=http://generation-service:8000\n"
        "VALIDATION_SERVICE_URL=http://validation-service:8000\n"
    )
    overrides = "services:\n"
    for service in BACKENDS:
        overrides += (
            f"  {service}:\n    env_file: !override\n"
            f"      - path: {json.dumps(str(directory / (service + '.env')))}\n"
            "        required: false\n"
        )
        if service == "application-api":
            overrides += '    ports: !override ["127.0.0.1::8000"]\n'
    (directory / "override.yaml").write_text(overrides)
    environment = Stack(directory)
    try:
        environment.run("up", "--build", "-d", "--wait", "--wait-timeout", "90")
        yield environment
    finally:
        # Only this randomly named test project and its disposable volume are removed.
        environment.run("down", "--volumes", "--remove-orphans")


def test_real_frontend_assets_and_backend_processes(stack: Stack):
    status, content_type, html = stack.get("/")
    assert status == 200
    assert content_type == "text/html"
    asset_path = re.search(r'src="(/assets/[^\"]+\.js)"', html)
    assert asset_path is not None
    assert stack.get(asset_path[1])[0] == 200
    assert json.loads(stack.get("/health/config")[2])["status"] == "valid"
    for service in BACKENDS:
        response = stack.run(
            "exec", "-T", "application-api", "python", "-c",
            f"import urllib.request; print(urllib.request.urlopen('http://{service}:8000/health/live').read().decode())",
        )
        assert json.loads(response) == {"status": "ok"}


def test_database_is_private_and_other_services_have_no_host_ports(stack: Stack):
    configuration = json.loads(stack.run("config", "--format", "json"))
    for service in ("generation-service", "validation-service", "app-db"):
        assert not configuration["services"][service].get("ports")
    assert set(configuration["services"]["app-db"]["networks"]) == {"database"}
    assert configuration["networks"]["database"]["internal"] is True
    for service in ("generation-service", "validation-service"):
        stack.run(
            "exec", "-T", service, "python", "-c",
            "import socket\ntry:\n socket.create_connection(('app-db', 5432), timeout=2)"
            "\nexcept OSError:\n pass\nelse:\n raise SystemExit('Unexpected database access')",
        )
    stack.run(
        "exec", "-T", "application-api", "python", "-c",
        "import socket; socket.create_connection(('app-db', 5432), timeout=2).close()",
    )
    assert stack.sql("SELECT 1;") == "1"


def test_database_volume_survives_container_recreation(stack: Stack):
    stack.sql("CREATE TABLE compose_probe (value integer); INSERT INTO compose_probe VALUES (37);")
    try:
        stack.run("rm", "--stop", "--force", "app-db")
        # An unavailable database must not disable the HTTP diagnostics or frontend.
        assert stack.get("/health/live")[0] == 200
        assert stack.get("/")[0] == 200
        stack.run("up", "-d", "--wait", "--wait-timeout", "90", "app-db")
        assert stack.sql("SELECT value FROM compose_probe;") == "37"
    finally:
        stack.sql("DROP TABLE IF EXISTS compose_probe;")


def test_missing_backend_env_keeps_diagnostics_available(stack: Stack):
    env_file = stack.directory / "application-api.env"
    contents = env_file.read_text()
    env_file.unlink()
    try:
        stack.run("up", "-d", "--force-recreate", "--no-deps", "--wait", "application-api")
        report = json.loads(stack.get("/health/config")[2])
        assert report["status"] == "invalid"
        assert {issue["field"] for issue in report["issues"]} == {
            "APP_DB_HOST", "APP_DB_PORT", "APP_DB_NAME", "APP_DB_USER", "APP_DB_PASSWORD",
            "GENERATION_SERVICE_URL", "VALIDATION_SERVICE_URL",
        }
        assert stack.get("/")[0] == 200
    finally:
        env_file.write_text(contents)
        stack.run("up", "-d", "--force-recreate", "--no-deps", "--wait", "application-api")


def test_explicit_container_environment_overrides_the_backend_file(stack: Stack):
    response = stack.run(
        "run", "--rm", "--no-deps", "-e", "APP_DB_PORT=bad", "application-api", "python", "-c",
        "import json; from application_api.config import load_config; print(json.dumps(load_config()[1]))",
    )
    report = json.loads(response)
    assert report["status"] == "invalid"
    assert report["issues"] == [
        {"field": "APP_DB_PORT", "code": "invalid", "message": "Nieprawidłowa wartość."}
    ]


def test_backend_images_do_not_contain_local_env_files(stack: Stack):
    for service in BACKENDS:
        stack.run(
            "exec", "-T", service, "python", "-c",
            "from pathlib import Path; assert not list(Path('/app').rglob('.env*'))",
        )
