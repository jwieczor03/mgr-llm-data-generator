from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from application_api.bootstrap import create_app


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
