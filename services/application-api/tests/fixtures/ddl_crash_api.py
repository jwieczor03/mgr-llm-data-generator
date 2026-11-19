"""Test-only subprocess executing real HTTP handlers until an injected crash point."""
import sys
import time
from pathlib import Path

from application_api.artifact_store import LocalArtifactStore
from application_api.bootstrap import create_app
from application_api.config import Settings
from application_api.database import Database
from application_api.ddl_config import DdlSettings
from application_api.ddl_repository import DdlRepository
from fastapi.testclient import TestClient

port, root, project, attempt, page, phase = sys.argv[1:]
root = Path(root)
settings = Settings(_env_file=None, app_db_host="127.0.0.1", app_db_port=port, app_db_name="testdb",
                    app_db_user="app_user", app_db_password="test:@/%$' secret")
database = Database(settings, {"blocked_capabilities": []})
database.start()
app = create_app()
app.state.database = database
app.state.ddl_settings = DdlSettings(_env_file=None)
app.state.ddl_runtime = root / "runtime"
app.state.artifacts = LocalArtifactStore(str(root / "project"), str(root / "working"))


def block():
    print("CRASH_POINT", flush=True)
    while True:
        time.sleep(60)


if phase == "journal":
    original = DdlRepository.journal
    def journal(*args, **kwargs):
        original(*args, **kwargs)
        block()
    DdlRepository.journal = journal
elif phase == "file":
    original = app.state.artifacts.put_at
    def put_at(*args, **kwargs):
        result = original(*args, **kwargs)
        block()
        return result
    app.state.artifacts.put_at = put_at
elif phase == "ack":
    original = DdlRepository.acknowledge
    def acknowledge(*args, **kwargs):
        result = original(*args, **kwargs)
        block()
        return result
    DdlRepository.acknowledge = acknowledge

client = TestClient(app)
path = f"/api/v1/projects/{project}/ddl-attempts/{attempt}"
result = client.post(path + "/files", files={"files": ("a.sql", b"SELECT 1")}, headers={"X-DDL-Page-ID": page})
if phase == "ack":
    assert result.status_code == 201
    client.post(path + "/receipt", json={"page_id": page, "receipt_nonce": result.json()["receipt_nonce"]})
raise SystemExit("crash point was not reached")
