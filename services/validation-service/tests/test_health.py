from fastapi.testclient import TestClient

from validation_service.bootstrap import app


def test_liveness():
    response = TestClient(app).get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_configuration_report():
    with TestClient(app) as client:
        response = client.get('/health/config')
    assert response.status_code == 200
    assert response.json() == {'service': 'validation-service', 'status': 'valid', 'issues': [], 'blocked_capabilities': []}
