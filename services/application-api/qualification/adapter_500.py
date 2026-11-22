import base64
import hashlib
import resource
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from application_api.ddl_process import WorkerProcess
from application_api.ddl_repository import PROFILE
from application_api.schema_contracts import DdlBundle, ManifestFile, manifest_digest


def ddl(n):
    fk = f", parent_id BIGINT REFERENCES sample_{n - 1}(id)" if n else ""
    return (
        f"CREATE TABLE sample_{n} (id BIGINT PRIMARY KEY, code VARCHAR(80) NOT NULL UNIQUE, "
        f"amount NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (amount >= 0), enabled BOOLEAN DEFAULT TRUE, "
        f"created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, description TEXT{fk});"
    )


contents = [
    "\n".join(ddl(n) for n in range(i * 50, (i + 1) * 50)).encode() for i in range(10)
]
files = [
    ManifestFile(
        file_id=uuid4(),
        name=f"schema_{i:02}.sql",
        position=i,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        artifact_id=uuid4(),
    )
    for i, data in enumerate(contents)
]
b = DdlBundle(
    schema_version_id=uuid4(), manifest_hash=manifest_digest(files), files=files
)
request = {
    "bundle": b.model_dump(mode="json"),
    "profile": PROFILE.model_dump(mode="json"),
    "files_base64": [base64.b64encode(x).decode() for x in contents],
    "checkpoint": None,
}
with tempfile.TemporaryDirectory(prefix="s2-t3-500-") as tmp:
    start = time.perf_counter()
    result = WorkerProcess(Path(tmp), timeout=120).run(request)
    elapsed = time.perf_counter() - start
    assert result.error is None, result.error
    ck = result.messages[0]["checkpoint"]["parsed"]
    assert (
        len(ck["tables"]) == 500
        and len(ck["relations"]) == 499
        and len(ck["diagnostics"]) == 0
    ), (len(ck["tables"]), len(ck["relations"]), ck["diagnostics"][:2])
    assert result.messages[1]["code"] == "DDL_ANALYZER_UNAVAILABLE"
    print(
        f"files={len(files)} bytes={sum(map(len, contents))} tables={len(ck['tables'])} columns={len(ck['columns'])} constraints={len(ck['constraints'])} relations={len(ck['relations'])} seconds={elapsed:.3f} child_peak_rss_platform_units={resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}"
    )
