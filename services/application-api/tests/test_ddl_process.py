import base64
import hashlib
import json
import os
import subprocess
import sys
from uuid import uuid4

from application_api.ddl_process import WorkerProcess
from application_api.ddl_repository import PROFILE
from application_api.schema_contracts import (
    Checkpoint,
    DdlBundle,
    ManifestFile,
    manifest_digest,
)


def test_production_worker_reports_analyzer_unavailable(tmp_path):
    content = b'CREATE TABLE t (id int);'
    file = ManifestFile(file_id=uuid4(), name='t.sql', position=0, size_bytes=len(content),
                        sha256=hashlib.sha256(content).hexdigest(), artifact_id=uuid4())
    bundle = DdlBundle(schema_version_id=uuid4(), manifest_hash=manifest_digest([file]), files=[file])
    request = {'bundle': bundle.model_dump(mode='json'), 'profile': PROFILE.model_dump(mode='json'),
               'files_base64': [base64.b64encode(content).decode()], 'checkpoint': None}
    result = WorkerProcess(tmp_path).run(request)
    assert result.error is None
    assert [message['type'] for message in result.messages] == ['checkpoint', 'error']
    assert Checkpoint.model_validate(result.messages[0]['checkpoint']).valid_for(bundle, PROFILE)
    assert result.messages[-1] == {'type': 'error', 'code': 'DDL_ANALYZER_UNAVAILABLE'}


def test_worker_audit_hook_blocks_socket_and_dns(tmp_path):
    script = '''
import socket
from application_api.ddl_worker import main

def adapter(_, emit):
    blocked = []
    for operation in (lambda: socket.socket(), lambda: socket.getaddrinfo("localhost", 80)):
        try:
            operation()
        except PermissionError:
            blocked.append(True)
    return {"blocked": blocked}
raise SystemExit(main(adapter))
'''
    read_fd, write_fd = os.pipe()
    try:
        process = subprocess.Popen([sys.executable, "-c", script, str(tmp_path / "lock"), str(read_fd), "10"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, pass_fds=(read_fd,))
        output, _ = process.communicate(b"{}", timeout=5)
        assert process.returncode == 0
        assert json.loads(output) == {"blocked": [True, True]}
    finally:
        os.close(read_fd)
        os.close(write_fd)


def test_worker_lock_parent_death_and_timeout(tmp_path):
    import select

    script = '''
import time
from application_api.ddl_worker import main

def adapter(_, emit):
    emit({"type": "started"})
    time.sleep(60)
    return {"type": "result"}
raise SystemExit(main(adapter))
'''
    lock = str(tmp_path / "worker.lock")
    handles = []

    def launch(timeout):
        read_fd, write_fd = os.pipe()
        process = subprocess.Popen([sys.executable, "-c", script, lock, str(read_fd), str(timeout)],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, pass_fds=(read_fd,))
        os.close(read_fd)
        process.stdin.write(b"{}")
        process.stdin.close()
        handles.append((process, write_fd))
        return process, write_fd

    try:
        first, parent1 = launch(10)
        assert json.loads(first.stdout.readline()) == {"type": "started"}
        second, _ = launch(2)
        assert not select.select([second.stdout], [], [], .2)[0]
        os.close(parent1)
        handles[0] = (first, None)
        assert first.wait(timeout=5) == 125
        assert json.loads(second.stdout.readline()) == {"type": "started"}
        assert second.wait(timeout=5) == 124
    finally:
        for process, fd in handles:
            if fd is not None:
                os.close(fd)
            if process.poll() is None:
                process.kill()
                process.wait()


def test_worker_does_not_inherit_database_or_llm_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PASSWORD", "test-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    script = '''
import os
from application_api.ddl_worker import main

def adapter(_, emit):
    return {"type": "result", "credentials_absent": not any(
        name in os.environ for name in ("APP_DB_PASSWORD", "OPENAI_API_KEY"))}
raise SystemExit(main(adapter))
'''
    outcome = WorkerProcess(tmp_path, command=[sys.executable, "-c", script]).run({})
    assert outcome.error is None
    assert outcome.messages == [{"type": "result", "credentials_absent": True}]


def test_large_checkpoint_is_drained_and_delivered_before_result(tmp_path):
    script = '''
from application_api.ddl_worker import main

def adapter(_, emit):
    emit({"type": "checkpoint", "data": "x" * 1048576})
    return {"type": "result"}
raise SystemExit(main(adapter))
'''
    messages = []
    result = WorkerProcess(tmp_path, timeout=5, command=[sys.executable, "-c", script]).run({}, messages.append)
    assert result.error is None
    assert [message["type"] for message in messages] == ["checkpoint", "result"]
    assert len(messages[0]["data"]) == 1048576
