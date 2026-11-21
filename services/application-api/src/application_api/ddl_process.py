"""Launch and supervise one DDL worker without inheriting credentials or sockets."""
import json
import os
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkerOutcome:
    messages: list[dict]
    error: str | None


class WorkerProcess:
    def __init__(self, runtime: Path, timeout: float = 120, command=None):
        self.runtime, self.timeout = runtime, timeout
        self.command = command or [sys.executable, "-m", "application_api.ddl_worker"]
        self.process = None
        self._guard = threading.Lock()

    def run(self, payload: dict, on_message=None) -> WorkerOutcome:
        read_fd, write_fd = os.pipe()
        try:
            with self._guard:
                self.process = subprocess.Popen(
                    [*self.command, str(self.runtime / "ddl-worker.lock"), str(read_fd), str(self.timeout)],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                    env={"PATH": os.defpath, "PYTHONUNBUFFERED": "1"}, pass_fds=(read_fd,),
                    close_fds=True, start_new_session=True,
                )
                process = self.process
            os.close(read_fd)
            read_fd = -1
            messages, errors = [], []

            def receive():
                try:
                    for line in process.stdout:
                        if not line.endswith(b"\n"):
                            raise ValueError("incomplete worker message")
                        message = json.loads(line)
                        if not isinstance(message, dict):
                            raise ValueError("invalid worker message")
                        # Checkpoints are persisted before receiving any later result.
                        if on_message is not None:
                            on_message(message)
                        messages.append(message)
                except Exception:
                    errors.append("DDL_WORKER_PROTOCOL_ERROR")
                    self.terminate()

            def send():
                try:
                    with process.stdin:
                        process.stdin.write(json.dumps(payload).encode())
                except (BrokenPipeError, OSError):
                    pass

            reader = threading.Thread(target=receive, daemon=True)
            writer = threading.Thread(target=send, daemon=True)
            reader.start()
            writer.start()
            try:
                process.wait(timeout=self.timeout + 1)
            except subprocess.TimeoutExpired:
                self.terminate()
                reader.join()
                writer.join()
                return WorkerOutcome([], "DDL_WORKER_TIMEOUT")
            reader.join()
            writer.join()
            if errors:
                return WorkerOutcome([], errors[0])
            if process.returncode != 0:
                return WorkerOutcome([], "DDL_WORKER_FAILED")
            if not messages:
                return WorkerOutcome([], "DDL_WORKER_PROTOCOL_ERROR")
            return WorkerOutcome(messages, None)
        except OSError:
            return WorkerOutcome([], "DDL_WORKER_FAILED")
        finally:
            if read_fd >= 0:
                os.close(read_fd)
            os.close(write_fd)
            with self._guard:
                self.process = None

    def terminate(self):
        with self._guard:
            process = self.process
        if process is None or process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
