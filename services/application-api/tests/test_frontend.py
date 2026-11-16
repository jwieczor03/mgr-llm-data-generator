from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from application_api import bootstrap, database
from application_api.bootstrap import create_app
from application_api.config import FIELDS, load_config


@pytest.fixture(autouse=True)
def isolate_lifespan(monkeypatch, tmp_path):
    # Frontend tests never consult the developer's environment or service .env.
    for name in FIELDS:
        monkeypatch.delenv(name.upper(), raising=False)
    isolated_config = load_config(tmp_path / "missing.env")
    monkeypatch.setattr(bootstrap, "load_config", lambda: isolated_config)

    def forbidden(*args, **kwargs):
        pytest.fail("Frontend tests must not create database engines or run migrations")

    monkeypatch.setattr(database, "create_engine", forbidden)
    monkeypatch.setattr(database.command, "upgrade", forbidden)


def test_lifespan_ignores_real_environment_and_service_env(monkeypatch, tmp_path):
    for key, value in {
        "APP_DB_HOST": "localhost", "APP_DB_PORT": "5432", "APP_DB_NAME": "local",
        "APP_DB_USER": "local-user", "APP_DB_PASSWORD": "local-password",
    }.items():
        monkeypatch.setenv(key, value)
    # Credentials injected after fixture setup must not reach the application.
    with TestClient(create_app(tmp_path)) as client:
        report = client.get("/health/database").json()
    assert report["migration_status"] == "not_run"
    assert report["issues"][0]["code"] == "configuration_missing"
    assert "local-password" not in str(report)


@pytest.fixture
def frontend(tmp_path: Path) -> Path:
    (tmp_path / "index.html").write_text('<html><script src="/assets/app.js"></script></html>')
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text('console.log("frontend");')
    return tmp_path


def test_serves_frontend_and_assets(frontend: Path):
    with TestClient(create_app(frontend)) as client:
        page = client.get("/")
        asset = client.get("/assets/app.js")
    assert page.status_code == 200
    assert page.headers["content-type"].startswith("text/html")
    assert '/assets/app.js' in page.text
    assert asset.status_code == 200
    assert asset.text == 'console.log("frontend");'
    assert "javascript" in asset.headers["content-type"]


@pytest.mark.parametrize("path", ["/api/v1/unknown", "/unknown-page", "/assets/missing.js"])
def test_missing_paths_do_not_fall_back_to_frontend(frontend: Path, path: str):
    with TestClient(create_app(frontend)) as client:
        response = client.get(path)
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


def test_assets_cannot_read_outside_the_asset_directory(frontend: Path):
    with TestClient(create_app(frontend)) as client:
        response = client.get("/assets/%2e%2e/index.html")
    assert response.status_code == 404


def test_diagnostics_remain_available_without_a_frontend_build(tmp_path: Path):
    with TestClient(create_app(tmp_path / "missing")) as client:
        assert client.get("/").status_code == 404
        assert client.get("/health/live").json() == {"status": "ok"}
        assert client.get("/health/config").status_code == 200
