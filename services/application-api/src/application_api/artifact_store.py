"""Logical artifact storage and a POSIX local implementation."""
import errno
import os
import stat
import uuid
from dataclasses import dataclass
from typing import Literal, Protocol

Namespace = Literal["project", "working"]


@dataclass(frozen=True)
class ArtifactRef:
    namespace: Namespace
    id: str


class ArtifactError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class ArtifactStore(Protocol):
    def put(self, namespace: Namespace, content: bytes) -> ArtifactRef: ...
    def get(self, ref: ArtifactRef) -> bytes: ...
    def delete(self, ref: ArtifactRef) -> bool: ...


def _error(exc: OSError, *, root: bool = False) -> ArtifactError:
    if exc.errno in (errno.EACCES, errno.EPERM):
        return ArtifactError("permission_denied")
    if exc.errno == errno.ENOENT:
        return ArtifactError("missing_root" if root else "not_found")
    if exc.errno in (errno.ELOOP, errno.ENOTDIR, errno.EISDIR):
        return ArtifactError("invalid_resource")
    return ArtifactError("io_error")


def _validate(ref: ArtifactRef) -> None:
    try:
        valid = (isinstance(ref, ArtifactRef) and ref.namespace in ("project", "working")
                 and isinstance(ref.id, str) and str(uuid.UUID(ref.id, version=4)) == ref.id)
    except (ValueError, AttributeError, TypeError):
        valid = False
    if not valid:
        raise ArtifactError("invalid_reference")


class LocalArtifactStore:
    def __init__(self, project_root: str, working_root: str):
        self.roots = {"project": project_root, "working": working_root}

    def _root(self, namespace: Namespace) -> int:
        if namespace not in self.roots:
            raise ArtifactError("invalid_reference")
        try:
            return os.open(self.roots[namespace], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as exc:
            raise _error(exc, root=True) from None

    def put(self, namespace: Namespace, content: bytes) -> ArtifactRef:
        fd = self._root(namespace)
        temp = f".tmp-{uuid.uuid4()}"
        created = False
        try:
            file_fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
            created = True
            with os.fdopen(file_fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            while True:
                ref = ArtifactRef(namespace, str(uuid.uuid4()))
                try:
                    # A hard link publishes complete bytes atomically without replacing a name.
                    os.link(temp, ref.id, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
                    break
                except FileExistsError:
                    continue
            return ref
        except OSError as exc:
            raise _error(exc) from None
        finally:
            if created:
                try:
                    os.unlink(temp, dir_fd=fd)
                except OSError:
                    pass
            os.close(fd)

    def get(self, ref: ArtifactRef) -> bytes:
        _validate(ref)
        root = self._root(ref.namespace)
        try:
            fd = os.open(ref.id, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=root)
            with os.fdopen(fd, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise ArtifactError("invalid_resource")
                return stream.read()
        except OSError as exc:
            raise _error(exc) from None
        finally:
            os.close(root)

    def delete(self, ref: ArtifactRef) -> bool:
        _validate(ref)
        root = self._root(ref.namespace)
        try:
            info = os.stat(ref.id, dir_fd=root, follow_symlinks=False)
            if not stat.S_ISREG(info.st_mode):
                raise ArtifactError("invalid_resource")
            os.unlink(ref.id, dir_fd=root)
            return True
        except FileNotFoundError:
            return False
        except OSError as exc:
            raise _error(exc) from None
        finally:
            os.close(root)

    def report(self) -> dict:
        results = {}
        for namespace in ("project", "working"):
            try:
                content = b"artifact-probe"
                ref = self.put(namespace, content)
                try:
                    if self.get(ref) != content:
                        raise ArtifactError("io_error")
                finally:
                    if not self.delete(ref):
                        raise ArtifactError("io_error")
                results[namespace] = {"status": "ready", "code": None}
            except ArtifactError as exc:
                results[namespace] = {"status": "unavailable", "code": exc.code}
        blocked = any(result["status"] != "ready" for result in results.values())
        return {"service": "application-api", "status": "unavailable" if blocked else "ready",
                "blocked_capabilities": ["artifacts"] if blocked else [], **results}


class UnconfiguredArtifactStore:
    def report(self) -> dict:
        result = {"status": "unavailable", "code": "configuration_unavailable"}
        return {"service": "application-api", "status": "unavailable", "blocked_capabilities": ["artifacts"],
                "project": result.copy(), "working": result.copy()}
