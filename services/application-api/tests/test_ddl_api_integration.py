import os
import time
import uuid

import pytest
from application_api.artifact_store import LocalArtifactStore
from application_api.bootstrap import create_app
from application_api.ddl_config import DdlSettings
from application_api.ddl_coordinator import DdlCoordinator
from fastapi.testclient import TestClient
from sqlalchemy import text

pytestmark = [pytest.mark.integration, pytest.mark.skipif(
    os.getenv("RUN_DATABASE_TESTS") != "1", reason="wymaga izolowanego Docker PostgreSQL")]


@pytest.fixture
def client(db, tmp_path):
    db.start()
    for name in ("project", "working", "runtime"):
        (tmp_path / name).mkdir()
    app = create_app()
    app.state.database = db
    app.state.ddl_settings = DdlSettings(_env_file=None)
    app.state.ddl_runtime = tmp_path / "runtime"
    app.state.artifacts = LocalArtifactStore(str(tmp_path / "project"), str(tmp_path / "working"))
    coord = DdlCoordinator(db, app.state.artifacts, app.state.ddl_runtime)
    coord.start()
    assert coord.ready_event.wait(5)
    app.state.ddl_coordinator = coord
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        coord.stop()


def wait_for(fn, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = fn()
        if value:
            return value
        time.sleep(.05)
    pytest.fail("timed out")


def test_upload_ack_retries_and_cancel(client, db):
    project = client.post("/api/v1/projects", json={"name": "DDL"}).json()["id"]
    root = f"/api/v1/projects/{project}"
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f"{root}/ddl-attempts/{attempt}"
    data = b"CREATE TABLE t (id int);"
    result = client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": len(data)}]})
    assert result.status_code == 201, result.text
    uploaded = client.post(path + "/files", files=[("files", ("a.sql", data, "application/sql"))],
                           headers={"X-DDL-Page-ID": page})
    assert uploaded.status_code == 201, uploaded.text
    state = client.get(path, headers={"X-DDL-Page-ID": page})
    assert state.json()["status"] == "STAGED"
    nonce = state.json()["receipt_nonce"]
    acknowledged = client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": nonce})
    assert acknowledged.status_code == 202, acknowledged.text
    version = acknowledged.json()["schema_version_id"]
    assert client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": nonce}).json()["schema_version_id"] == version
    assert client.get(f"{root}/schema-versions/{version}/files/" + client.get(f"{root}/schema-versions/{version}").json()["files"][0]["id"]).content == data

    checkpoints = []

    def advance():
        state = client.get(path).json()
        if state["status"] == "RETRY_WAIT":
            with db.session() as session:
                checkpoint = session.execute(text("SELECT checkpoint FROM app.ddl_attempts WHERE id=:id"),
                                             {"id": uuid.UUID(attempt)}).scalar_one()
                assert checkpoint is not None
                assert checkpoint["parsed"]["tables"][0]["name"] == "t"
                assert checkpoint["analysis_profile"]["library_version"] == "8.9"
                checkpoints.append(checkpoint)
                session.execute(text("UPDATE app.ddl_attempts SET next_attempt_at=now() WHERE id=:id"), {"id": uuid.UUID(attempt)})
        return state if state["status"] == "FAILED_TECHNICAL" else None

    terminal = wait_for(advance)
    assert terminal["launch_count"] == 4
    assert checkpoints and all(item == checkpoints[0] for item in checkpoints)
    repeated_upload = client.post(path + "/files", files=[("files", ("a.sql", data))],
                                  headers={"X-DDL-Page-ID": page})
    assert repeated_upload.status_code == 409
    assert repeated_upload.json()["error"]["code"] == "DDL_UPLOAD_ALREADY_RECEIVED"
    assert repeated_upload.json()["error"]["details"]["status_url"] == path
    assert client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": nonce}).json()["schema_version_id"] == version
    assert client.get(f"{root}/schema-versions/{version}/analysis").status_code == 409
    attempt2, page2 = str(uuid.uuid4()), str(uuid.uuid4())
    path2 = f"{root}/ddl-attempts/{attempt2}"
    assert client.put(path2, json={"page_id": page2, "files": [{"name": "b.sql", "size_bytes": 1}]}).status_code == 201
    assert client.post(path2 + "/cancel", json={"page_id": page2}).status_code == 202
    wait_for(lambda: client.get(path2).json().get("status") == "CANCELLED")


def test_invalid_bundle_and_truncated_multipart_never_create_version(client, db):
    project = client.post("/api/v1/projects", json={"name": "Invalid"}).json()["id"]
    root = f"/api/v1/projects/{project}"
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f"{root}/ddl-attempts/{attempt}"
    files = [("same.sql", b"\xff"), ("SAME.SQL", b"-- only comment"), ("literal.sql", b"SELECT $$--literal$$;")]
    meta = [{"name": name, "size_bytes": len(content)} for name, content in files]
    assert client.put(path, json={"page_id": page, "files": meta}).status_code == 201
    result = client.post(path + "/files", files=[("files", (name, content)) for name, content in files],
                         headers={"X-DDL-Page-ID": page})
    assert result.status_code == 422, result.text
    assert {item["code"] for item in result.json()["error"]["details"]["diagnostics"]} == {
        "DDL_INVALID_ENCODING", "DDL_EMPTY_FILE", "DDL_DUPLICATE_FILENAME"}
    wait_for(lambda: client.get(path).json().get("status") == "REJECTED_INPUT")
    assert client.get(root + "/schema-versions").json()["items"] == []
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f"{root}/ddl-attempts/{attempt}"
    assert client.put(path, json={"page_id": page, "files": [{"name": "x.sql", "size_bytes": 8}]}).status_code == 201
    body = b'--abc\r\nContent-Disposition: form-data; name="files"; filename="x.sql"\r\n\r\nSELECT 1'
    result = client.post(path + "/files", content=body,
                         headers={"X-DDL-Page-ID": page, "Content-Type": "multipart/form-data; boundary=abc"})
    assert result.status_code == 409, result.text
    wait_for(lambda: client.get(path).json().get("status") == "CANCELLED")
    with db.session() as session:
        assert session.execute(text("SELECT count(*) FROM app.schema_versions")).scalar_one() == 0


def test_500_table_bundle_acceptance_measurement(client):
    import resource
    import tracemalloc

    project = client.post("/api/v1/projects", json={"name": "500 tables"}).json()["id"]
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f"/api/v1/projects/{project}/ddl-attempts/{attempt}"
    def ddl(n):
        foreign_key = f", parent_id BIGINT REFERENCES sample_{n - 1}(id)" if n else ""
        return (f"CREATE TABLE sample_{n} (id BIGINT PRIMARY KEY, code VARCHAR(80) NOT NULL UNIQUE, "
                f"amount NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (amount >= 0), enabled BOOLEAN DEFAULT TRUE, "
                f"created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, description TEXT{foreign_key});")

    files = [(f"schema_{i:02}.sql", "\n".join(ddl(n) for n in range(i * 50, (i + 1) * 50)).encode())
             for i in range(10)]
    size = sum(len(data) for _, data in files)
    reservation = {"page_id": page, "files": [{"name": name, "size_bytes": len(data)} for name, data in files]}
    tracemalloc.start()
    start = time.perf_counter()
    assert client.put(path, json=reservation).status_code == 201
    response = client.post(path + "/files", files=[("files", (name, data)) for name, data in files],
                           headers={"X-DDL-Page-ID": page})
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert response.status_code == 201, response.text
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"DDL_ACCEPT_500 bytes={size} files={len(files)} seconds={elapsed:.3f} peak_python_bytes={peak} "
          f"process_peak_rss_platform_units={rss}")
    assert client.post(path + "/cancel", json={"page_id": page}).status_code == 202
    wait_for(lambda: client.get(path).json().get("status") == "CANCELLED")


def test_partial_cleanup_holds_slot_until_retry(client, db, monkeypatch):
    from application_api.artifact_store import ArtifactError

    project = client.post("/api/v1/projects", json={"name": "Cleanup"}).json()["id"]
    root = f"/api/v1/projects/{project}"
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f"{root}/ddl-attempts/{attempt}"
    meta = [{"name": "a.sql", "size_bytes": 8}, {"name": "b.sql", "size_bytes": 8}]
    assert client.put(path, json={"page_id": page, "files": meta}).status_code == 201
    uploaded = client.post(path + "/files", files=[("files", ("a.sql", b"SELECT 1")), ("files", ("b.sql", b"SELECT 2"))],
                           headers={"X-DDL-Page-ID": page})
    assert uploaded.status_code == 201
    store = client.app.state.artifacts
    original = store.delete
    calls = 0

    def fail_second(ref):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ArtifactError("io_error")
        return original(ref)

    monkeypatch.setattr(store, "delete", fail_second)
    assert client.post(path + "/cancel", json={"page_id": page}).status_code == 202
    wait_for(lambda: client.get(path).json().get("status") == "CLEANUP_FAILED")
    other = f"{root}/ddl-attempts/{uuid.uuid4()}"
    response = client.put(other, json={"page_id": str(uuid.uuid4()), "files": meta})
    assert response.status_code == 409 and response.json()["error"]["code"] == "DDL_PROCESSING_IN_PROGRESS"
    monkeypatch.setattr(store, "delete", original)
    with db.session() as session:
        session.execute(text("UPDATE app.ddl_attempts SET next_attempt_at=now() WHERE id=:id"), {"id": uuid.UUID(attempt)})
    wait_for(lambda: client.get(path).json().get("status") == "CANCELLED")
    assert list((client.app.state.ddl_runtime.parent / "project").iterdir()) == []
    assert client.get(root + "/schema-versions").json()["items"] == []


def test_restart_expires_unacknowledged_staged_bundle(client, db):
    project = client.post("/api/v1/projects", json={"name": "Restart"}).json()["id"]
    root = f"/api/v1/projects/{project}"
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f"{root}/ddl-attempts/{attempt}"
    assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
    assert client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")}, headers={"X-DDL-Page-ID": page}).status_code == 201
    client.app.state.ddl_coordinator.stop()
    replacement = DdlCoordinator(db, client.app.state.artifacts, client.app.state.ddl_runtime)
    replacement.start()
    try:
        assert replacement.ready_event.wait(5)
        wait_for(lambda: client.get(path).json().get("status") == "EXPIRED")
        assert client.get(root + "/schema-versions").json()["items"] == []
        assert list((client.app.state.ddl_runtime.parent / "project").iterdir()) == []
    finally:
        replacement.stop()


def test_real_worker_with_test_adapter_publishes_and_rejects(client, db):
    import sys
    from pathlib import Path

    from application_api.ddl_process import WorkerProcess

    app = client.app
    app.state.ddl_coordinator.stop()
    helper = str(Path(__file__).parent / "fixtures" / "ddl_test_worker.py")

    def coordinator(mode):
        def factory(runtime, timeout):
            return WorkerProcess(runtime, timeout, [sys.executable, helper, mode])
        instance = DdlCoordinator(db, app.state.artifacts, app.state.ddl_runtime, worker_factory=factory)
        instance.start()
        assert instance.ready_event.wait(5)
        return instance

    project = client.post("/api/v1/projects", json={"name": "Adapter"}).json()["id"]
    root = f"/api/v1/projects/{project}"

    def upload_and_ack():
        attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
        path = f"{root}/ddl-attempts/{attempt}"
        assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
        result = client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")}, headers={"X-DDL-Page-ID": page})
        assert result.status_code == 201
        result = client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": result.json()["receipt_nonce"]})
        return path, result.json()["schema_version_id"]

    first = coordinator("success")
    try:
        path, version1 = upload_and_ack()
        wait_for(lambda: client.get(path).json().get("status") == "SUCCEEDED")
        assert client.get(f"{root}/schema-versions/{version1}/analysis").json()["supported"] is True
    finally:
        first.stop()
    second = coordinator("reject")
    try:
        path, version2 = upload_and_ack()
        wait_for(lambda: client.get(path).json().get("status") == "REJECTED_DDL")
        assert client.get(f"{root}/schema-versions/{version2}/analysis").json()["supported"] is False
        with db.session() as session:
            assert str(session.execute(text("SELECT default_schema_version_id FROM app.projects WHERE id=:id"),
                                       {"id": uuid.UUID(project)}).scalar_one()) == version1
    finally:
        second.stop()


def test_checkpoint_persisted_before_worker_exit_and_resumed_after_restart(client, db):
    import sys
    from pathlib import Path

    from application_api.ddl_process import WorkerProcess

    app = client.app
    app.state.ddl_coordinator.stop()
    helper = str(Path(__file__).parent / "fixtures" / "ddl_test_worker.py")

    def start(mode):
        def factory(runtime, timeout):
            return WorkerProcess(runtime, timeout, [sys.executable, helper, mode])
        coord = DdlCoordinator(db, app.state.artifacts, app.state.ddl_runtime, worker_factory=factory)
        coord.start()
        assert coord.ready_event.wait(5)
        return coord

    waiting = start("wait")
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    try:
        project = client.post("/api/v1/projects", json={"name": "Checkpoint"}).json()["id"]
        path = f"/api/v1/projects/{project}/ddl-attempts/{attempt}"
        assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
        stage = client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")}, headers={"X-DDL-Page-ID": page})
        assert client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": stage.json()["receipt_nonce"]}).status_code == 202

        def checkpoint_saved():
            with db.session() as session:
                return session.execute(text("SELECT checkpoint IS NOT NULL FROM app.ddl_attempts WHERE id=:id"),
                                       {"id": uuid.UUID(attempt)}).scalar_one()

        wait_for(checkpoint_saved)
        assert waiting.worker.process.poll() is None
    finally:
        waiting.stop()
    with db.session() as session:
        session.execute(text("UPDATE app.ddl_attempts SET next_attempt_at=now() WHERE id=:id AND status='RETRY_WAIT'"),
                        {"id": uuid.UUID(attempt)})
    resumed = start("resume")
    try:
        wait_for(lambda: client.get(path).json().get("status") == "SUCCEEDED")
        assert client.get(path).json()["launch_count"] == 2
    finally:
        resumed.stop()


def test_cross_process_io_lock_fences_upload_after_cancel(client):
    import subprocess
    import sys
    from concurrent.futures import ThreadPoolExecutor

    from application_api.artifact_store import ArtifactRef
    from application_api.ddl_api import publish_file
    from application_api.ddl_input import InputError
    from application_api.ddl_repository import DdlRepository

    app = client.app
    project = client.post("/api/v1/projects", json={"name": "Race"}).json()["id"]
    attempt, page = uuid.uuid4(), uuid.uuid4()
    path = f"/api/v1/projects/{project}/ddl-attempts/{attempt}"
    assert client.put(path, json={"page_id": str(page), "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
    repo = DdlRepository(app.state.database)
    _, epoch = repo.start_receiving(uuid.UUID(project), attempt, page)
    script = '''
import sys
from pathlib import Path
from application_api.ddl_runtime import io_lock
with io_lock(Path(sys.argv[1])):
    print("locked", flush=True)
    sys.stdin.read(1)
'''
    holder = subprocess.Popen([sys.executable, "-c", script, str(app.state.ddl_runtime)],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        assert holder.stdout.readline() == b"locked\n"
        with ThreadPoolExecutor(max_workers=1) as pool:
            ref = ArtifactRef("project", str(uuid.uuid4()))
            future = pool.submit(publish_file, repo, app.state.artifacts, app.state.ddl_runtime,
                                 uuid.UUID(project), attempt, epoch, ref, b"SELECT 1")
            assert client.post(path + "/cancel", json={"page_id": str(page)}).status_code == 202
            holder.stdin.write(b"x")
            holder.stdin.flush()
            with pytest.raises(InputError, match="DDL_ATTEMPT_CLOSED"):
                future.result(timeout=5)
        wait_for(lambda: client.get(path).json().get("status") == "CANCELLED")
        assert list((app.state.ddl_runtime.parent / "project").iterdir()) == []
    finally:
        holder.kill() if holder.poll() is None else None
        holder.wait(timeout=5)


@pytest.mark.parametrize("phase", ["journal", "file", "ack"])
def test_sigkill_api_at_journal_file_and_ack(client, db, postgres, phase):
    import select
    import subprocess
    import sys
    from pathlib import Path

    app = client.app
    app.state.ddl_coordinator.stop()
    project = client.post("/api/v1/projects", json={"name": "Crash " + phase}).json()["id"]
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    root = f"/api/v1/projects/{project}"
    path = f"{root}/ddl-attempts/{attempt}"
    assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
    script = str(Path(__file__).parent / "fixtures" / "ddl_crash_api.py")
    child = subprocess.Popen([sys.executable, script, str(postgres[1]), str(app.state.ddl_runtime.parent),
                              project, attempt, page, phase], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        ready, _, _ = select.select([child.stdout], [], [], 10)
        assert ready and child.stdout.readline() == b"CRASH_POINT\n", child.stderr.read().decode() if child.poll() is not None else "no crash point"
        child.kill()
        child.wait(timeout=5)
        replacement = DdlCoordinator(db, app.state.artifacts, app.state.ddl_runtime)
        replacement.start()
        try:
            assert replacement.ready_event.wait(5)
            if phase != "ack":
                wait_for(lambda: client.get(path).json().get("status") == "EXPIRED")
                assert client.get(root + "/schema-versions").json()["items"] == []
                assert list((app.state.ddl_runtime.parent / "project").iterdir()) == []
            else:
                def terminal():
                    state = client.get(path).json()
                    if state["status"] == "RETRY_WAIT":
                        with db.session() as session:
                            session.execute(text("UPDATE app.ddl_attempts SET next_attempt_at=now() WHERE id=:id"),
                                            {"id": uuid.UUID(attempt)})
                    return state if state["status"] == "FAILED_TECHNICAL" else None
                state = wait_for(terminal)
                version = state["schema_version_id"]
                manifest = client.get(f"{root}/schema-versions/{version}").json()["files"]
                assert client.get(f"{root}/schema-versions/{version}/files/{manifest[0]['id']}").content == b"SELECT 1"
        finally:
            replacement.stop()
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=5)


def test_sigkill_coordinator_after_checkpoint_and_resume(client, db, postgres):
    import select
    import subprocess
    import sys
    from pathlib import Path

    from application_api.ddl_process import WorkerProcess

    app = client.app
    app.state.ddl_coordinator.stop()
    project = client.post("/api/v1/projects", json={"name": "Killed leader"}).json()["id"]
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f"/api/v1/projects/{project}/ddl-attempts/{attempt}"
    assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
    stage = client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")}, headers={"X-DDL-Page-ID": page})
    assert client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": stage.json()["receipt_nonce"]}).status_code == 202
    folder = Path(__file__).parent / "fixtures"
    child = subprocess.Popen([sys.executable, str(folder / "ddl_crash_coordinator.py"), str(postgres[1]),
                              str(app.state.ddl_runtime.parent), attempt], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        ready, _, _ = select.select([child.stdout], [], [], 10)
        assert ready and child.stdout.readline() == b"CHECKPOINT_SAVED\n", child.stderr.read().decode() if child.poll() is not None else "checkpoint timeout"
        child.kill()
        child.wait(timeout=5)
        helper = str(folder / "ddl_test_worker.py")
        def factory(runtime, timeout):
            return WorkerProcess(runtime, timeout, [sys.executable, helper, "resume"])
        new = DdlCoordinator(db, app.state.artifacts, app.state.ddl_runtime, worker_factory=factory)
        new.start()
        try:
            assert new.ready_event.wait(5)
            wait_for(lambda: client.get(path).json().get("status") == "SUCCEEDED")
            assert client.get(path).json()["launch_count"] == 2
        finally:
            new.stop()
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=5)


def test_owner_project_and_nonce_isolation(client):
    from types import SimpleNamespace

    from application_api.identity import ActorContext

    project = client.post("/api/v1/projects", json={"name": "Owner"}).json()["id"]
    path = f"/api/v1/projects/{project}/ddl-attempts/{uuid.uuid4()}"
    page = str(uuid.uuid4())
    assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
    staged = client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")}, headers={"X-DDL-Page-ID": page})
    nonce = staged.json()["receipt_nonce"]
    assert client.get(path, headers={"X-DDL-Page-ID": str(uuid.uuid4())}).status_code == 409
    wrong = client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": "not-the-nonce"})
    assert wrong.status_code == 409 and wrong.json()["error"]["code"] == "DDL_RECEIPT_CONFLICT"
    client.app.state.actor_context_provider = SimpleNamespace(get_context=lambda: ActorContext("other-owner"))
    assert client.get(path, headers={"X-DDL-Page-ID": page}).status_code == 404
    assert client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": nonce}).status_code == 404
    client.app.state.actor_context_provider = SimpleNamespace(get_context=lambda: ActorContext("local-owner"))
    assert client.post(path + "/cancel", json={"page_id": page}).status_code == 202
    wait_for(lambda: client.get(path).json().get("status") == "CANCELLED")


def test_coordinator_recovers_after_database_session_is_killed(client, db):
    import sys
    from pathlib import Path

    from application_api.ddl_coordinator import COORDINATOR_LOCK_KEY
    from application_api.ddl_process import WorkerProcess

    app = client.app
    app.state.ddl_coordinator.stop()
    helper = str(Path(__file__).parent / "fixtures" / "ddl_test_worker.py")
    launches = []

    def factory(runtime, timeout):
        launches.append(1)
        return WorkerProcess(runtime, timeout, [sys.executable, helper, "wait" if len(launches) == 1 else "resume"])

    coordinator = DdlCoordinator(db, app.state.artifacts, app.state.ddl_runtime, worker_factory=factory)
    coordinator.start()
    assert coordinator.ready_event.wait(5)
    try:
        project = client.post("/api/v1/projects", json={"name": "Lost connection"}).json()["id"]
        attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
        path = f"/api/v1/projects/{project}/ddl-attempts/{attempt}"
        assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
        stage = client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")}, headers={"X-DDL-Page-ID": page})
        assert client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": stage.json()["receipt_nonce"]}).status_code == 202

        def saved():
            with db.session() as session:
                return session.execute(text("SELECT checkpoint IS NOT NULL FROM app.ddl_attempts WHERE id=:id"),
                                       {"id": uuid.UUID(attempt)}).scalar_one()

        wait_for(saved)
        with db.engine.begin() as connection:
            pid = connection.execute(text("""SELECT pid FROM pg_locks WHERE locktype='advisory'
                AND granted AND classid=0 AND objid=:key AND objsubid=1"""), {"key": COORDINATOR_LOCK_KEY}).scalar_one()
            assert connection.execute(text("SELECT pg_terminate_backend(:pid)"), {"pid": pid}).scalar_one()
        wait_for(lambda: client.get(path).json().get("status") == "SUCCEEDED")
        assert client.get(path).json()["launch_count"] == 2
    finally:
        coordinator.stop()


def test_late_upload_failure_after_receipt_does_not_cancel_accepted_version(client, monkeypatch):
    import threading
    from concurrent.futures import ThreadPoolExecutor

    from application_api.ddl_repository import DdlRepository

    client.app.state.ddl_coordinator.stop()
    project = client.post("/api/v1/projects", json={"name": "Late upload failure"}).json()["id"]
    root = f"/api/v1/projects/{project}"
    path = f"{root}/ddl-attempts/{uuid.uuid4()}"
    page = str(uuid.uuid4())
    assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
    staged, release = threading.Event(), threading.Event()
    original = DdlRepository.staged

    def stage_then_fail(*args, **kwargs):
        original(*args, **kwargs)
        staged.set()
        assert release.wait(5)
        raise OSError("lost upload response")

    monkeypatch.setattr(DdlRepository, "staged", stage_then_fail)
    with ThreadPoolExecutor(max_workers=1) as pool:
        upload = pool.submit(client.post, path + "/files", files={"files": ("a.sql", b"SELECT 1")},
                             headers={"X-DDL-Page-ID": page})
        try:
            assert staged.wait(5)
            state = client.get(path, headers={"X-DDL-Page-ID": page}).json()
            assert state["status"] == "STAGED"
            ack = client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": state["receipt_nonce"]})
            assert ack.status_code == 202
        finally:
            release.set()
        assert upload.result(timeout=5).status_code == 500
    version = ack.json()["schema_version_id"]
    assert client.get(path).json()["status"] == "ANALYSIS_PENDING"
    assert client.get(f"{root}/schema-versions/{version}").status_code == 200
    assert client.get(root + "/ddl-processing").json()["busy"] is True


def test_invalid_utf8_json_uses_validation_error_envelope(client):
    path = f"/api/v1/projects/{uuid.uuid4()}/ddl-attempts/{uuid.uuid4()}"
    response = client.put(path, content=b"\xff", headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.headers["X-Request-ID"] == response.json()["error"]["request_id"]


def test_version_views_follow_attempt_state_through_cleanup(client, db):
    from application_api.ddl_repository import DdlRepository

    client.app.state.ddl_coordinator.stop()
    project = client.post("/api/v1/projects", json={"name": "Version status"}).json()["id"]
    root = f"/api/v1/projects/{project}"
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f"{root}/ddl-attempts/{attempt}"
    assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
    stage = client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")}, headers={"X-DDL-Page-ID": page})
    version = client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": stage.json()["receipt_nonce"]}).json()["schema_version_id"]
    version_path = f"{root}/schema-versions/{version}"
    repo = DdlRepository(db)

    def verify(status):
        operation = client.get(path).json()
        detail = client.get(version_path).json()
        items = client.get(root + "/schema-versions").json()["items"]
        assert operation["status"] == detail["status"] == items[0]["status"] == status
        assert operation["diagnostics"] == detail["diagnostics"] == items[0]["diagnostics"]

    verify("ANALYSIS_PENDING")
    launch = repo.launch(uuid.UUID(attempt))
    verify("ANALYZING")
    repo.worker_failed(uuid.UUID(attempt), launch["epoch"], "DDL_WORKER_FAILED")
    verify("RETRY_WAIT")
    assert client.post(path + "/cancel").status_code == 202
    verify("CANCELLING")
    repo.cleanup_failed(uuid.UUID(attempt))
    verify("CLEANUP_FAILED")
    for artifact in repo.cleanup_files(uuid.UUID(attempt)):
        from application_api.artifact_store import ArtifactRef
        client.app.state.artifacts.delete(ArtifactRef("project", str(artifact)))
    repo.finish_cleanup(uuid.UUID(attempt))
    assert client.get(version_path).status_code == 404
    assert client.get(root + "/schema-versions").json()["items"] == []


def test_slow_content_validation_does_not_block_other_api_requests(client, monkeypatch):
    import asyncio
    import threading

    import httpx
    from application_api import ddl_api

    project = client.post("/api/v1/projects", json={"name": "Responsive"}).json()["id"]
    root = f"/api/v1/projects/{project}"
    path = f"{root}/ddl-attempts/{uuid.uuid4()}"
    page = str(uuid.uuid4())
    assert client.put(path, json={"page_id": page, "files": [{"name": "a.sql", "size_bytes": 8}]}).status_code == 201
    entered, release = threading.Event(), threading.Event()
    timed_out = []
    original = ddl_api.validate_content

    def controlled_validation(contents):
        entered.set()
        if not release.wait(4):
            timed_out.append(True)
        return original(contents)

    monkeypatch.setattr(ddl_api, "validate_content", controlled_validation)

    async def scenario():
        transport = httpx.ASGITransport(app=client.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
            upload = asyncio.create_task(async_client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")},
                                                            headers={"X-DDL-Page-ID": page}))
            try:
                assert await asyncio.to_thread(entered.wait, 2)
                response = await asyncio.wait_for(async_client.get(root + "/ddl-processing"), timeout=2)
                assert response.status_code == 200 and response.json()["busy"]
                assert not timed_out
            finally:
                release.set()
                await upload

    asyncio.run(scenario())
    assert client.post(path + "/cancel", json={"page_id": page}).status_code == 202
    wait_for(lambda: client.get(path).json().get("status") == "CANCELLED")


def test_invalid_numeric_parameter_reaches_persisted_worker_checkpoint(client, db):
    project = client.post('/api/v1/projects', json={'name': 'Invalid numeric'}).json()['id']
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f'/api/v1/projects/{project}/ddl-attempts/{attempt}'
    data = b'CREATE TABLE t(a numeric(-1));'
    assert client.put(path, json={'page_id': page, 'files': [{'name': 'x.sql', 'size_bytes': len(data)}]}).status_code == 201
    uploaded = client.post(path + '/files', files=[('files', ('x.sql', data, 'application/sql'))],
                           headers={'X-DDL-Page-ID': page})
    assert uploaded.status_code == 201
    nonce = client.get(path, headers={'X-DDL-Page-ID': page}).json()['receipt_nonce']
    assert client.post(path + '/receipt', json={'page_id': page, 'receipt_nonce': nonce}).status_code == 202

    def read_checkpoint():
        with db.session() as session:
            return session.execute(text('SELECT checkpoint FROM app.ddl_attempts WHERE id=:id'),
                                   {'id': uuid.UUID(attempt)}).scalar_one()

    checkpoint = wait_for(read_checkpoint)
    assert [item['code'] for item in checkpoint['parsed']['diagnostics']] == ['DDL_UNSUPPORTED_TYPE']


@pytest.mark.parametrize(('data', 'expected_codes', 'expected_constraint'), [
    (b'CREATE TABLE t(id int PRIMARY KEY DEFAULT 1, name text CONSTRAINT nn NOT NULL);', [], 'not_null'),
    (b'CREATE TABLE t(id int);\x00CREATE VIEW v AS SELECT 1;', ['DDL_SYNTAX_ERROR'], None),
])
def test_parser_worker_persists_primary_key_not_null_and_nul(client, db, data, expected_codes, expected_constraint):
    project = client.post('/api/v1/projects', json={'name': 'Parser checkpoint'}).json()['id']
    attempt, page = str(uuid.uuid4()), str(uuid.uuid4())
    path = f'/api/v1/projects/{project}/ddl-attempts/{attempt}'
    assert client.put(path, json={'page_id': page, 'files': [{'name': 'x.sql', 'size_bytes': len(data)}]}).status_code == 201
    uploaded = client.post(path + '/files', files=[('files', ('x.sql', data, 'application/sql'))],
                           headers={'X-DDL-Page-ID': page})
    assert uploaded.status_code == 201
    nonce = client.get(path, headers={'X-DDL-Page-ID': page}).json()['receipt_nonce']
    assert client.post(path + '/receipt', json={'page_id': page, 'receipt_nonce': nonce}).status_code == 202

    def read_checkpoint():
        with db.session() as session:
            return session.execute(text('SELECT checkpoint FROM app.ddl_attempts WHERE id=:id'),
                                   {'id': uuid.UUID(attempt)}).scalar_one()

    checkpoint = wait_for(read_checkpoint)
    assert checkpoint['analysis_profile']['adapter_version'] == 'pglast-2'
    assert [item['code'] for item in checkpoint['parsed']['diagnostics']] == expected_codes
    if expected_constraint:
        constraint = next(c for c in checkpoint['parsed']['constraints'] if c['kind'] == expected_constraint)
        assert constraint['name'] == 'nn'
        assert checkpoint['parsed']['columns'][0]['default']['literal_value'] == '1'
