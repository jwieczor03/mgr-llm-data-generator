from application_api.bootstrap import create_app
from fastapi.testclient import TestClient


def test_ready_reports_missing_configuration_without_secret(monkeypatch):
    monkeypatch.setenv("APP_DB_PASSWORD", "secret-test-value")
    with TestClient(create_app()) as client:
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["scope"] == "foundation"
        assert data["capacity"] in ("partial", "incapable")
        assert "secret-test-value" not in response.text
        assert {x["id"] for x in data["checks"]} == {"process", "configuration", "database", "artifacts", "generation", "validation"}
