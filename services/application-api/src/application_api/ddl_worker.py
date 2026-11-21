"""Isolated worker entry point. It never receives application credentials."""
import fcntl
import json
import os
import select
import stat
import sys
import threading
import time


def _audit(event, _args):
    if event.startswith("socket.") or event in {
        "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.fork", "os.forkpty",
    }:
        raise PermissionError("operation forbidden in DDL worker")


def _watch_parent(fd: int, timeout: float):
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            os._exit(124)
        readable, _, _ = select.select([fd], [], [], remaining)
        if readable and not os.read(fd, 1):
            os._exit(125)


def main(analyze=None):
    if len(sys.argv) != 4:
        return 2
    lock_path, parent_fd, timeout = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    threading.Thread(target=_watch_parent, args=(parent_fd, timeout), daemon=True).start()
    # The lock is held until process exit, including timeout and parent death.
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a+b") as lock:
        if not stat.S_ISREG(os.fstat(lock.fileno()).st_mode):
            return 2
        fcntl.flock(lock, fcntl.LOCK_EX)
        sys.addaudithook(_audit)
        request = json.load(sys.stdin)
        # T3 and T4 are not implemented yet: never report a fabricated analysis.
        def emit(message):
            print(json.dumps(message), flush=True)

        if analyze is None:
            from application_api.ddl_worker_analysis import analyze as default_analyze
            analyze = default_analyze
        result = analyze(request, emit)
        emit(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
