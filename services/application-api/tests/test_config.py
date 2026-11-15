from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from application_api.config import FIELDS, load_config, require_capabilities


VALUES = {
    'APP_DB_HOST': 'localhost', 'APP_DB_PORT': '5432', 'APP_DB_NAME': 'app',
    'APP_DB_USER': 'user', 'APP_DB_PASSWORD': 'secret-value',
    'GENERATION_SERVICE_URL': 'http://localhost:8001',
    'VALIDATION_SERVICE_URL': 'http://localhost:8002',
}


def setup_env(monkeypatch, tmp_path):
    for name in FIELDS:
        monkeypatch.delenv(name.upper(), raising=False)
    path = tmp_path / '.env'
    path.write_text(''.join(f'{key}={value}\n' for key, value in VALUES.items()))
    return path


def test_environment_precedence_and_secret(monkeypatch, tmp_path):
    path = setup_env(monkeypatch, tmp_path)
    monkeypatch.setenv('APP_DB_PORT', '5555')
    settings, report = load_config(path)
    assert settings.app_db_port == 5555
    assert report['status'] == 'valid'
    assert 'secret-value' not in repr(settings)
    assert 'secret-value' not in repr(report)


def test_invalid_one_area_preserves_others(monkeypatch, tmp_path):
    path = setup_env(monkeypatch, tmp_path)
    monkeypatch.setenv('APP_DB_PORT', 'invalid-secret-value')
    settings, report = load_config(path)
    assert settings.generation_service_url == VALUES['GENERATION_SERVICE_URL']
    assert report['blocked_capabilities'] == ['database']
    assert 'invalid-secret-value' not in repr(report)
    assert report['issues'][0]['field'] == 'APP_DB_PORT'


def test_missing_and_invalid_urls(monkeypatch, tmp_path):
    path = setup_env(monkeypatch, tmp_path)
    monkeypatch.setenv('GENERATION_SERVICE_URL', 'http://user:password@host/path')
    monkeypatch.setenv('APP_DB_PASSWORD', '')
    _, report = load_config(path)
    assert set(report['blocked_capabilities']) == {'database', 'generation'}
    assert 'password@host' not in repr(report)


def test_guard_blocks_only_affected_capability():
    app = FastAPI()
    app.state.config_report = {'blocked_capabilities': ['database']}
    @app.get('/db', dependencies=[Depends(require_capabilities('database'))])
    def db():
        return {'ok': True}
    @app.get('/generation', dependencies=[Depends(require_capabilities('generation'))])
    def generation():
        return {'ok': True}
    with TestClient(app) as client:
        assert client.get('/db').status_code == 503
        assert client.get('/generation').status_code == 200


def test_report_http_and_restart(monkeypatch, tmp_path):
    import os
    import shutil
    import socket
    import subprocess
    import sys
    import time
    import httpx

    service_dir = tmp_path / 'service'
    shutil.copytree(__import__('pathlib').Path(__file__).resolve().parents[1] / 'src', service_dir / 'src')
    env_file = service_dir / '.env'
    env_file.write_text(''.join(f'{key}={value}\n' for key, value in VALUES.items()))
    env = os.environ.copy()
    for key in VALUES:
        env.pop(key, None)
    env['PYTHONPATH'] = str(service_dir / 'src')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]

    def start():
        process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'application_api.bootstrap:app', '--host', '127.0.0.1', '--port', str(port)], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                response = httpx.get(f'http://127.0.0.1:{port}/health/config', timeout=0.2)
                return process, response.json()
            except httpx.TransportError:
                if process.poll() is not None:
                    raise AssertionError('server exited')
                time.sleep(0.05)
        process.terminate()
        raise AssertionError('server did not start')

    process, report = start()
    try:
        assert report['status'] == 'valid'
        env_file.write_text('APP_DB_PORT=bad\n')
        assert httpx.get(f'http://127.0.0.1:{port}/health/config').json() == report
        assert httpx.get(f'http://127.0.0.1:{port}/health/live').json() == {'status': 'ok'}
    finally:
        process.terminate()
        process.wait(timeout=5)
    process, report = start()
    try:
        assert report['status'] == 'invalid'
        assert set(report['blocked_capabilities']) == {'database', 'generation', 'validation'}
    finally:
        process.terminate()
        process.wait(timeout=5)


def test_port_and_host_boundaries(monkeypatch, tmp_path):
    path = setup_env(monkeypatch, tmp_path)
    for value in ('0', '65536', '1.0', '-1'):
        monkeypatch.setenv('APP_DB_PORT', value)
        _, report = load_config(path)
        assert report['blocked_capabilities'] == ['database']
    monkeypatch.setenv('APP_DB_PORT', '65535')
    monkeypatch.setenv('APP_DB_HOST', '::1')
    assert load_config(path)[1]['status'] == 'valid'


def test_invalid_password_never_logged(monkeypatch, tmp_path, caplog):
    path = setup_env(monkeypatch, tmp_path)
    monkeypatch.setenv('GENERATION_SERVICE_URL', 'http://secret-marker@example.com')
    with caplog.at_level('DEBUG'):
        _, report = load_config(path)
    assert 'secret-marker' not in str(report)
    assert 'secret-marker' not in caplog.text
    assert 'secret-value' not in caplog.text


def test_url_with_empty_userinfo_is_invalid(monkeypatch, tmp_path):
    path = setup_env(monkeypatch, tmp_path)
    monkeypatch.setenv('GENERATION_SERVICE_URL', 'http://@localhost:8001')
    assert load_config(path)[1]['blocked_capabilities'] == ['generation']
