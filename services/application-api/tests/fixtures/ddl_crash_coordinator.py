"""Test-only coordinator process waiting after checkpoint persistence."""
import sys
import time
from pathlib import Path
from uuid import UUID

from application_api.artifact_store import LocalArtifactStore
from application_api.config import Settings
from application_api.database import Database
from application_api.ddl_coordinator import DdlCoordinator
from application_api.ddl_process import WorkerProcess
from sqlalchemy import text

port, root, attempt = sys.argv[1:]
root = Path(root)
settings = Settings(_env_file=None, app_db_host="127.0.0.1", app_db_port=port, app_db_name="testdb",
                    app_db_user="app_user", app_db_password="test:@/%$' secret")
database = Database(settings, {"blocked_capabilities": []})
database.start()
helper = str(Path(__file__).parent / "ddl_test_worker.py")
store = LocalArtifactStore(str(root / "project"), str(root / "working"))
def factory(runtime, timeout):
    return WorkerProcess(runtime, timeout, [sys.executable, helper, "wait"])
coord = DdlCoordinator(database, store, root / "runtime", worker_factory=factory)
coord.start()
assert coord.ready_event.wait(5)
while True:
    with database.session() as session:
        checkpoint = session.execute(text("SELECT checkpoint IS NOT NULL FROM app.ddl_attempts WHERE id=:id"),
                                     {"id": UUID(attempt)}).scalar_one()
    if checkpoint:
        print("CHECKPOINT_SAVED", flush=True)
        while True:
            time.sleep(60)
    time.sleep(.05)
