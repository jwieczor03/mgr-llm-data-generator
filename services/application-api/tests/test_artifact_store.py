import errno
import os
import uuid

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from application_api.artifact_store import ArtifactError, ArtifactRef, LocalArtifactStore
from application_api.bootstrap import create_app
from application_api.config import load_config, require_capabilities


@pytest.fixture(autouse=True)
def isolate_database_configuration(monkeypatch, tmp_path):
    for name in ("APP_DB_HOST", "APP_DB_PORT", "APP_DB_NAME", "APP_DB_USER", "APP_DB_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    # Do not read a developer's local service .env while testing runtime diagnostics.
    import application_api.bootstrap as bootstrap
    original = bootstrap.load_config
    monkeypatch.setattr(bootstrap, "load_config", lambda: original(tmp_path / "absent.env"))


@pytest.fixture
def store(tmp_path):
    project, working = tmp_path / 'project', tmp_path / 'working'
    project.mkdir()
    working.mkdir()
    return LocalArtifactStore(str(project), str(working))


def consume(store):
    ref = store.put('project', b'\x00\xffdata')
    assert store.get(ref) == b'\x00\xffdata'
    assert store.delete(ref) is True
    assert store.delete(ref) is False


def test_contract_and_isolation(store):
    class MemoryStore:
        def __init__(self): self.data = {}
        def put(self, namespace, content):
            ref = ArtifactRef(namespace, str(uuid.uuid4()))
            self.data[ref] = content
            return ref
        def get(self, ref): return self.data[ref]
        def delete(self, ref): return self.data.pop(ref, None) is not None
    consume(MemoryStore())
    consume(store)
    a = store.put('project', b'a')
    b = store.put('working', b'b')
    assert store.delete(a)
    assert store.get(b) == b'b'
    with pytest.raises(ArtifactError, match='not_found'):
        store.get(a)


@pytest.mark.parametrize('ref', [ArtifactRef('project', '../x'), ArtifactRef('project', '/tmp/x'),
                                 ArtifactRef('other', str(uuid.uuid4())), ArtifactRef('working', str(uuid.uuid1()))])
def test_invalid_references(store, ref):
    for operation in (store.get, store.delete):
        with pytest.raises(ArtifactError, match='invalid_reference'):
            operation(ref)


def test_symlink_and_nonfile(store, tmp_path):
    outside = tmp_path / 'outside'
    outside.write_bytes(b'secret')
    ref = ArtifactRef('project', str(uuid.uuid4()))
    target = tmp_path / 'project' / ref.id
    target.symlink_to(outside)
    for operation in (store.get, store.delete):
        with pytest.raises(ArtifactError, match='invalid_resource'):
            operation(ref)
    assert outside.read_bytes() == b'secret'
    target.unlink()
    target.mkdir()
    for operation in (store.get, store.delete):
        with pytest.raises(ArtifactError, match='invalid_resource'):
            operation(ref)
    (tmp_path / 'working').rmdir()
    (tmp_path / 'working').symlink_to(tmp_path / 'project', target_is_directory=True)
    with pytest.raises(ArtifactError, match='invalid_resource'):
        store.put('working', b'x')


def test_fault_before_publish_and_cleanup_failure(store, tmp_path, monkeypatch):
    old = store.put('project', b'old')
    real_link = os.link
    def fail(*args, **kwargs): raise OSError(errno.EIO, 'private path')
    monkeypatch.setattr(os, 'link', fail)
    with pytest.raises(ArtifactError, match='io_error') as exc:
        store.put('project', b'partial')
    assert 'private path' not in str(exc.value)
    assert store.get(old) == b'old'
    assert len(list((tmp_path / 'project').iterdir())) == 1
    monkeypatch.setattr(os, 'link', real_link)
    real_unlink = os.unlink
    def fail_temp(path, *args, **kwargs):
        if str(path).startswith('.tmp-'): raise OSError(errno.EIO, 'private')
        return real_unlink(path, *args, **kwargs)
    monkeypatch.setattr(os, 'unlink', fail_temp)
    ref = store.put('project', b'complete')
    assert store.get(ref) == b'complete'
    with pytest.raises(ArtifactError, match='invalid_reference'):
        store.get(ArtifactRef('project', next(p.name for p in (tmp_path / 'project').iterdir() if p.name.startswith('.tmp-'))))


def test_missing_root_and_permission_error(store, tmp_path, monkeypatch):
    (tmp_path / 'project').rmdir()
    ref = ArtifactRef('project', str(uuid.uuid4()))
    for operation in (store.get, store.delete):
        with pytest.raises(ArtifactError, match='missing_root'): operation(ref)
    real_open = os.open
    def denied(path, *args, **kwargs):
        if path == store.roots['working']: raise PermissionError(errno.EACCES, 'secret')
        return real_open(path, *args, **kwargs)
    monkeypatch.setattr(os, 'open', denied)
    assert store.report()['working']['code'] == 'permission_denied'


def test_configuration_and_runtime_health(monkeypatch, tmp_path):
    project, working = tmp_path / 'project', tmp_path / 'working'
    for root in (project, working): root.mkdir()
    monkeypatch.setenv('ARTIFACT_PROJECT_ROOT', str(project))
    monkeypatch.setenv('ARTIFACT_WORKING_ROOT', str(working))
    app = create_app()
    @app.get('/protected', dependencies=[Depends(require_capabilities('artifacts'))])
    def protected(): return {'ok': True}
    with TestClient(app) as client:
        assert client.get('/health/artifacts').json()['status'] == 'ready'
        assert client.get('/protected').status_code == 200
        project.rmdir()
        result = client.get('/health/artifacts').json()
        assert result['project']['code'] == 'missing_root'
        assert str(tmp_path) not in str(result)
        assert client.get('/protected').json()['detail']['code'] == 'artifacts_unavailable'
        assert client.get('/health/live').status_code == 200
        project.mkdir()
        assert client.get('/protected').status_code == 200
    monkeypatch.setenv('ARTIFACT_WORKING_ROOT', str(project / 'nested'))
    assert 'artifacts' in load_config(tmp_path / 'absent')[1]['blocked_capabilities']
    with TestClient(create_app()) as client:
        assert client.get('/health/artifacts').json()['project']['code'] == 'configuration_unavailable'


def test_collision_and_delete_failure(store, monkeypatch):
    old = store.put('project', b'old')
    values = iter([uuid.uuid4(), uuid.UUID(old.id), uuid.uuid4()])
    monkeypatch.setattr(uuid, 'uuid4', lambda: next(values))
    new = store.put('project', b'new')
    assert new != old and store.get(old) == b'old' and store.get(new) == b'new'
    def fail(*args, **kwargs): raise OSError(errno.EACCES, 'private')
    monkeypatch.setattr(os, 'unlink', fail)
    with pytest.raises(ArtifactError, match='permission_denied'):
        store.delete(old)
    assert store.get(old) == b'old'


def test_fsync_failure_does_not_publish(store, tmp_path, monkeypatch):
    old = store.put('working', b'old')
    def fail(_): raise OSError(errno.EIO, 'private')
    monkeypatch.setattr(os, 'fsync', fail)
    with pytest.raises(ArtifactError, match='io_error'):
        store.put('working', b'new')
    assert store.get(old) == b'old'
    assert [p.name for p in (tmp_path / 'working').iterdir()] == [old.id]


def test_configuration_guard(monkeypatch, tmp_path):
    monkeypatch.setenv('ARTIFACT_PROJECT_ROOT', 'relative')
    monkeypatch.setenv('ARTIFACT_WORKING_ROOT', str(tmp_path))
    app = create_app()
    @app.get('/protected', dependencies=[Depends(require_capabilities('artifacts'))])
    def protected(): return {'ok': True}
    with TestClient(app) as client:
        result = client.get('/protected')
        assert result.status_code == 503
        assert result.json()['detail']['code'] == 'configuration_unavailable'


@pytest.mark.parametrize('suffix', ['/', '/.', '//./', '/nested/..'])
def test_root_symlink_with_suffix_is_rejected_across_runtime(monkeypatch, tmp_path, suffix):
    project, working = tmp_path / 'project', tmp_path / 'working'
    project.mkdir()
    working.mkdir()
    monkeypatch.setenv('ARTIFACT_PROJECT_ROOT', str(project) + suffix)
    monkeypatch.setenv('ARTIFACT_WORKING_ROOT', str(working) + suffix)
    app = create_app()

    @app.get('/protected', dependencies=[Depends(require_capabilities('artifacts'))])
    def protected(): return {'ok': True}

    with TestClient(app) as client:
        assert client.get('/health/artifacts').json()['status'] == 'ready'
        assert client.get('/protected').status_code == 200
        ref = app.state.artifacts.put('project', b'private')
        working.rmdir()
        working.symlink_to(project, target_is_directory=True)
        report = client.get('/health/artifacts').json()
        assert report['project'] == {'status': 'ready', 'code': None}
        assert report['working'] == {'status': 'unavailable', 'code': 'invalid_resource'}
        assert str(tmp_path) not in str(report)
        response = client.get('/protected')
        assert response.status_code == 503
        assert response.json()['detail']['code'] == 'artifacts_unavailable'
        wrong_namespace = ArtifactRef('working', ref.id)
        for operation in (app.state.artifacts.get, app.state.artifacts.delete):
            with pytest.raises(ArtifactError, match='invalid_resource'):
                operation(wrong_namespace)
        assert app.state.artifacts.get(ref) == b'private'
        working.unlink()
        working.mkdir()
        assert client.get('/health/artifacts').json()['status'] == 'ready'
        assert client.get('/protected').status_code == 200


@pytest.mark.parametrize('working_suffix', ['/./', '/child/..', '/nested/../subdir'])
def test_configuration_rejects_roots_overlapping_after_normalization(monkeypatch, tmp_path, working_suffix):
    monkeypatch.setenv('ARTIFACT_PROJECT_ROOT', str(tmp_path / 'project') + '/.')
    monkeypatch.setenv('ARTIFACT_WORKING_ROOT', str(tmp_path / 'project') + working_suffix)
    assert 'artifacts' in load_config(tmp_path / 'absent.env')[1]['blocked_capabilities']
