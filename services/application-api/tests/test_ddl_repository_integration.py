import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from application_api.ddl_input import InputError
from application_api.ddl_repository import DdlRepository
from sqlalchemy import text

pytestmark = [pytest.mark.integration, pytest.mark.skipif(
    os.getenv("RUN_DATABASE_TESTS") != "1", reason="wymaga izolowanego Docker PostgreSQL")]


def test_reservation_and_ack_are_serialized(db):
    db.start()
    project, page = uuid.uuid4(), uuid.uuid4()
    with db.session() as session:
        session.execute(text("INSERT INTO app.projects (id,owner_subject,name,name_key,created_at) VALUES (:id,'o','p','p',now())"),
                        {"id": project})
    repo = DdlRepository(db)
    files = [{"name": "a.sql", "size_bytes": 8}]
    attempts = [uuid.uuid4(), uuid.uuid4()]

    def reserve(attempt):
        try:
            repo.reserve(project, "o", attempt, page, files)
            return attempt
        except InputError as exc:
            assert exc.code == "DDL_PROCESSING_IN_PROGRESS"
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        accepted = [value for value in pool.map(reserve, attempts) if value]
    assert len(accepted) == 1
    attempt = accepted[0]
    assert repo.reserve(project, "o", attempt, page, files) is False
    reservation, epoch = repo.start_receiving(project, attempt, page)
    assert reservation == files
    artifact = uuid.uuid4()
    repo.journal(project, attempt, epoch, artifact)
    nonce = repo.staged(project, attempt, epoch, [{"id": uuid.uuid4(), "position": 0, "name": "a.sql",
                                                   "size_bytes": 8, "sha256": "0" * 64, "artifact_id": artifact}])
    with ThreadPoolExecutor(max_workers=2) as pool:
        versions = list(pool.map(lambda _: repo.acknowledge(project, attempt, page, nonce), range(2)))
    assert versions[0] == versions[1]
    with db.session() as session:
        assert session.execute(text("SELECT count(*) FROM app.schema_versions")).scalar_one() == 1
        assert session.execute(text("SELECT receipt_nonce FROM app.ddl_attempts WHERE id=:id"), {"id": attempt}).scalar_one() is None
    with pytest.raises(InputError, match="DDL_RECEIPT_CONFLICT"):
        repo.acknowledge(project, attempt, page, "wrong")


def test_retry_deadlines_are_durable_and_maximum_is_four(db):
    from datetime import datetime, timezone

    db.start()
    project, page, attempt, artifact = (uuid.uuid4() for _ in range(4))
    with db.session() as session:
        session.execute(text("INSERT INTO app.projects (id,owner_subject,name,name_key,created_at) VALUES (:id,'o','p','p',now())"), {"id": project})
    repo = DdlRepository(db)
    repo.reserve(project, "o", attempt, page, [{"name": "a.sql", "size_bytes": 8}])
    _, epoch = repo.start_receiving(project, attempt, page)
    repo.journal(project, attempt, epoch, artifact)
    nonce = repo.staged(project, attempt, epoch, [{"id": uuid.uuid4(), "position": 0, "name": "a.sql", "size_bytes": 8,
                                                  "sha256": "0" * 64, "artifact_id": artifact}])
    repo.acknowledge(project, attempt, page, nonce)
    for count, delay in enumerate((1, 5, 15, None), start=1):
        launch = repo.launch(attempt)
        assert launch["launch_count"] == count
        before = datetime.now(timezone.utc)
        repo.worker_failed(attempt, launch["epoch"], "DDL_ANALYZER_UNAVAILABLE")
        with db.session() as session:
            row = session.execute(text("SELECT status, next_attempt_at FROM app.ddl_attempts WHERE id=:id"), {"id": attempt}).first()
            if delay is not None:
                assert row.status == "RETRY_WAIT"
                assert 0 <= (row.next_attempt_at - before).total_seconds() - delay < 1
                assert session.execute(text("SELECT attempt_id FROM app.ddl_slot WHERE singleton=1")).scalar_one() == attempt
                session.execute(text("UPDATE app.ddl_attempts SET next_attempt_at=now() WHERE id=:id"), {"id": attempt})
            else:
                assert row.status == "FAILED_TECHNICAL"
                assert session.execute(text("SELECT attempt_id FROM app.ddl_slot WHERE singleton=1")).scalar_one() is None
