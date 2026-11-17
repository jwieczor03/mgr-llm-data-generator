from application_api.bootstrap import app
from fastapi.testclient import TestClient


def test_liveness():
    response = TestClient(app).get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_api_is_json_404():
    response = TestClient(app).get("/api/v1/unknown")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
