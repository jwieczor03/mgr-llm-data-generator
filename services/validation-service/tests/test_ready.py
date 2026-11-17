from fastapi.testclient import TestClient
from validation_service.bootstrap import app


def test_ready_reports_foundation_only():
    with TestClient(app) as client:
        data = client.get("/health/ready").json()
        assert data["capacity"] == "capable"
        assert data["scope"] == "foundation"
        assert any("szkieletem" in item for item in data["limitations"])
