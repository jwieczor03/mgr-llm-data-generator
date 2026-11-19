"""PostgreSQL constraints for DDL attempts and versions."""
import os
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

pytestmark = [pytest.mark.integration, pytest.mark.skipif(
    os.getenv("RUN_DATABASE_TESTS") != "1", reason="wymaga izolowanego Docker PostgreSQL")]


def test_ddl_schema_constraints(db):
    db.start()
    assert db.migration_status == "applied"
    project, other, attempt, version = (uuid.uuid4() for _ in range(4))
    with db.session() as session:
        for index, identifier in enumerate((project, other)):
            session.execute(text("""INSERT INTO app.projects
                (id, owner_subject, name, name_key, created_at)
                VALUES (:id, 'owner', :name, :name, now())"""),
                {"id": identifier, "name": f"project{index}"})
        session.execute(text("""INSERT INTO app.ddl_attempts
            (id, project_id, owner_subject, page_id, reservation, reservation_hash, status)
            VALUES (:id, :project, 'owner', :page, '[]'::jsonb, :hash, 'RESERVED')"""),
            {"id": attempt, "project": project, "page": uuid.uuid4(), "hash": "0" * 64})
        session.execute(text("""INSERT INTO app.schema_versions
            (id, project_id, attempt_id, revision_no, manifest_hash, analysis_profile, status)
            VALUES (:id, :project, :attempt, 1, :hash, 'profile', 'ANALYSIS_PENDING')"""),
            {"id": version, "project": project, "attempt": attempt, "hash": "0" * 64})
    with pytest.raises(IntegrityError), db.session() as session:
        session.execute(text("UPDATE app.projects SET default_schema_version_id=:version WHERE id=:project"),
                        {"version": version, "project": other})
    with pytest.raises(IntegrityError), db.session() as session:
        session.execute(text("INSERT INTO app.ddl_slot (singleton) VALUES (2)"))
    with pytest.raises(IntegrityError), db.session() as session:
        session.execute(text("UPDATE app.ddl_attempts SET launch_count=5 WHERE id=:attempt"), {"attempt": attempt})
