import os

import pytest
from application_api.ddl_coordinator import COORDINATOR_LOCK_KEY
from application_api.ddl_leader import LeaderDatabase
from sqlalchemy import text

pytestmark = [pytest.mark.integration, pytest.mark.skipif(
    os.getenv("RUN_DATABASE_TESTS") != "1", reason="wymaga izolowanego Docker PostgreSQL")]


def test_leader_heartbeat_and_lock_release(db):
    db.start()
    with db.engine.connect() as connection:
        connection.detach()
        assert connection.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": COORDINATOR_LOCK_KEY}).scalar_one()
        connection.commit()
        leader = LeaderDatabase(connection, COORDINATOR_LOCK_KEY)
        leader.heartbeat()
        leader.retire()
    with db.engine.connect() as connection:
        assert connection.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": COORDINATOR_LOCK_KEY}).scalar_one()
        connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": COORDINATOR_LOCK_KEY})


def prepared(db):
    import uuid

    from application_api.ddl_repository import PROFILE, DdlRepository
    from application_api.schema_contracts import SchemaAnalysis

    project, attempt, page, artifact = (uuid.uuid4() for _ in range(4))
    with db.session() as session:
        session.execute(text("INSERT INTO app.projects (id,owner_subject,name,name_key,created_at) VALUES (:id,'o','p','p',now())"), {"id": project})
    repo = DdlRepository(db)
    repo.reserve(project, "o", attempt, page, [{"name": "a.sql", "size_bytes": 8}])
    _, epoch = repo.start_receiving(project, attempt, page)
    repo.journal(project, attempt, epoch, artifact)
    nonce = repo.staged(project, attempt, epoch, [{"id": uuid.uuid4(), "position": 0, "name": "a.sql",
                                                  "size_bytes": 8, "sha256": "0" * 64, "artifact_id": artifact}])
    repo.acknowledge(project, attempt, page, nonce)
    connection = db.engine.connect()
    connection.detach()
    assert connection.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": COORDINATOR_LOCK_KEY}).scalar_one()
    connection.commit()
    leader = LeaderDatabase(connection, COORDINATOR_LOCK_KEY)
    leader_repo = DdlRepository(leader)
    launch = leader_repo.launch(attempt)
    bundle = leader_repo.bundle(attempt, launch["version"])
    analysis = SchemaAnalysis(contract_version=1, schema_version_id=bundle.schema_version_id, analysis_profile=PROFILE,
                              tables=[], columns=[], constraints=[], relations=[], diagnostics=[], supported=True)
    return project, attempt, leader, leader_repo, launch, bundle, PROFILE, analysis


def terminate(db, leader):
    with db.engine.begin() as connection:
        assert connection.execute(text("SELECT pg_terminate_backend(:pid)"), {"pid": leader.pid}).scalar_one()


def test_lost_session_blocks_old_checkpoint_and_result_without_new_epoch(db):
    import hashlib

    from application_api.schema_contracts import (
        Checkpoint,
        ParsedSchema,
        canonical_json,
    )

    db.start()
    project, attempt, leader, repo, launch, bundle, profile, analysis = prepared(db)
    parsed = ParsedSchema(schema_version_id=bundle.schema_version_id, tables=[], columns=[], constraints=[], relations=[], diagnostics=[])
    checkpoint = Checkpoint(contract_version=1, schema_version_id=bundle.schema_version_id, manifest_hash=bundle.manifest_hash,
                            analysis_profile=profile, parsed=parsed,
                            model_hash=hashlib.sha256(canonical_json(parsed.model_dump(mode="json"))).hexdigest())
    terminate(db, leader)
    for action in (lambda: repo.save_checkpoint(attempt, launch["epoch"], bundle, profile, checkpoint),
                   lambda: repo.publish(attempt, launch["epoch"], bundle, profile, analysis),
                   lambda: repo.worker_failed(attempt, launch["epoch"], "fail")):
        with pytest.raises(Exception):
            action()
    with db.session() as session:
        row = session.execute(text("SELECT status, execution_epoch, checkpoint FROM app.ddl_attempts WHERE id=:id"), {"id": attempt}).first()
        assert row == ("ANALYZING", launch["epoch"], None)
        assert session.execute(text("SELECT default_schema_version_id FROM app.projects WHERE id=:id"), {"id": project}).scalar_one() is None
        assert session.execute(text("SELECT attempt_id FROM app.ddl_slot WHERE singleton=1")).scalar_one() == attempt
    leader.retire()
    leader.connection.close()


def test_commit_succeeded_before_session_loss_remains_single_result(db):
    db.start()
    project, attempt, leader, repo, launch, bundle, profile, analysis = prepared(db)
    repo.publish(attempt, launch["epoch"], bundle, profile, analysis)
    terminate(db, leader)
    leader.retire()
    leader.connection.close()
    with db.session() as session:
        assert session.execute(text("SELECT status FROM app.ddl_attempts WHERE id=:id"), {"id": attempt}).scalar_one() == "SUCCEEDED"
        assert session.execute(text("SELECT default_schema_version_id FROM app.projects WHERE id=:id"), {"id": project}).scalar_one() == bundle.schema_version_id
        assert session.execute(text("SELECT count(*) FROM app.schema_interpretations")).scalar_one() == 1
        assert session.execute(text("SELECT attempt_id FROM app.ddl_slot WHERE singleton=1")).scalar_one() is None


def test_session_dies_after_dml_before_commit_rolls_back(db):
    import threading
    from concurrent.futures import ThreadPoolExecutor

    db.start()
    project, attempt, leader, repo, launch, bundle, profile, analysis = prepared(db)
    written, continue_commit = threading.Event(), threading.Event()

    def interrupted_transaction():
        with leader.session() as session:
            session.execute(text("UPDATE app.ddl_attempts SET status='SUCCEEDED' WHERE id=:id"), {"id": attempt})
            session.execute(text("UPDATE app.projects SET default_schema_version_id=:version WHERE id=:id"),
                            {"id": project, "version": bundle.schema_version_id})
            written.set()
            assert continue_commit.wait(5)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(interrupted_transaction)
        assert written.wait(5)
        terminate(db, leader)
        continue_commit.set()
        with pytest.raises(Exception):
            future.result(timeout=5)
    with db.session() as session:
        assert session.execute(text("SELECT status FROM app.ddl_attempts WHERE id=:id"), {"id": attempt}).scalar_one() == "ANALYZING"
        assert session.execute(text("SELECT default_schema_version_id FROM app.projects WHERE id=:id"), {"id": project}).scalar_one() is None
    leader.connection.close()


def test_retired_generation_cannot_write_after_new_election(db):
    db.start()
    project, attempt, old, repo, launch, bundle, profile, analysis = prepared(db)
    old.retire()
    old.connection.close()
    with db.engine.connect() as connection:
        connection.detach()
        assert connection.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": COORDINATOR_LOCK_KEY}).scalar_one()
        connection.commit()
        new = LeaderDatabase(connection, COORDINATOR_LOCK_KEY)
        with pytest.raises(Exception):
            repo.publish(attempt, launch["epoch"], bundle, profile, analysis)
        new.heartbeat()
        new.retire()
    with db.session() as session:
        assert session.execute(text("SELECT status FROM app.ddl_attempts WHERE id=:id"), {"id": attempt}).scalar_one() == "ANALYZING"


def test_lost_commit_ack_recovers_from_durable_state(db, monkeypatch):
    from application_api.ddl_repository import DdlRepository
    from sqlalchemy.exc import OperationalError

    db.start()
    project, attempt, leader, repo, launch, bundle, profile, analysis = prepared(db)
    dialect = db.engine.dialect
    commit = dialect.do_commit

    def committed_then_disconnected(connection):
        commit(connection)
        raise OperationalError("COMMIT", {}, RuntimeError("lost commit acknowledgement"))

    with monkeypatch.context() as patch:
        patch.setattr(dialect, "do_commit", committed_then_disconnected)
        with pytest.raises(OperationalError):
            repo.publish(attempt, launch["epoch"], bundle, profile, analysis)
    leader.retire()
    leader.connection.close()
    with db.engine.connect() as connection:
        connection.detach()
        assert connection.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": COORDINATOR_LOCK_KEY}).scalar_one()
        connection.commit()
        new = LeaderDatabase(connection, COORDINATOR_LOCK_KEY)
        assert DdlRepository(new).current() is None
        new.retire()
    with db.session() as session:
        assert session.execute(text("SELECT count(*) FROM app.schema_interpretations")).scalar_one() == 1
        assert session.execute(text("SELECT status FROM app.ddl_attempts WHERE id=:id"), {"id": attempt}).scalar_one() == "SUCCEEDED"
