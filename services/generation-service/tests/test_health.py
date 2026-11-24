import pytest
from fastapi.testclient import TestClient
from generation_service.bootstrap import app


def test_liveness():
    response = TestClient(app).get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_configuration_report():
    with TestClient(app) as client:
        response = client.get('/health/config')
        assert app.state.llm_client_factory is None
    assert response.status_code == 200
    assert response.json() == {'service': 'generation-service', 'status': 'valid', 'issues': [], 'blocked_capabilities': []}


def test_optional_llm_configuration(monkeypatch):
    monkeypatch.setenv('LLM_BACKEND', 'external')
    monkeypatch.setenv('LLM_BASE_URL', 'https://example.invalid/v1')
    monkeypatch.setenv('LLM_API_KEY', 'fake-secret')
    with TestClient(app) as client:
        assert client.get('/health/config').json()['status'] == 'valid'
        assert app.state.llm_client_factory is not None
        first = app.state.llm_client_factory()
        second = app.state.llm_client_factory()
        first.attempts.append(object())
        assert len(first.attempts) == 1
        assert second.attempts == []
        assert 'fake-secret' not in repr(app.state.settings)
        assert 'fake-secret' not in str(app.state.settings.model_dump())
        assert 'fake-secret' not in client.get('/health/config').text


def test_invalid_llm_configuration_does_not_expose_values(monkeypatch):
    monkeypatch.setenv('LLM_BACKEND', 'external')
    monkeypatch.setenv('LLM_BASE_URL', 'http://example.invalid/v1')
    monkeypatch.setenv('LLM_API_KEY', 'fake-secret')
    with TestClient(app) as client:
        response = client.get('/health/config')
        assert response.json()['status'] == 'invalid'
        assert response.json()['blocked_capabilities'] == ['llm']
        assert app.state.llm_client_factory is None
        assert 'fake-secret' not in response.text


def test_empty_llm_setting_activates_validation(monkeypatch):
    monkeypatch.setenv('LLM_BACKEND', '')
    with TestClient(app) as client:
        assert client.get('/health/config').json()['status'] == 'invalid'
        assert app.state.llm_client_factory is None


@pytest.mark.parametrize('url', ['https://example.invalid/\npath', 'https://example.invalid?',
                                 'https://example.invalid#', 'https://@example.invalid'])
def test_malformed_url_is_rejected_without_network(monkeypatch, url):
    monkeypatch.setenv('LLM_BACKEND', 'external')
    monkeypatch.setenv('LLM_BASE_URL', url)
    monkeypatch.setenv('LLM_API_KEY', 'fake-secret')
    with TestClient(app) as client:
        assert client.get('/health/config').json()['status'] == 'invalid'
        assert app.state.llm_client_factory is None
