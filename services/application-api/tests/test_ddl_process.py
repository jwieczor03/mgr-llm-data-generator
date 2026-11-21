import json
import os
import subprocess
import sys

from application_api.ddl_process import WorkerProcess


def test_production_worker_reports_analyzer_unavailable(tmp_path):
    result = WorkerProcess(tmp_path).run({"files": []})
    assert result.error is None
    assert result.messages == [{"type": "error", "code": "DDL_ANALYZER_UNAVAILABLE"}]


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
