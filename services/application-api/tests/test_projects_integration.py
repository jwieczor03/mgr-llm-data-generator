import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from application_api.bootstrap import create_app
from application_api.database import Database
from application_api.identity import ActorContext
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

pytestmark = [pytest.mark.integration, pytest.mark.skipif(__import__("os").getenv("RUN_DATABASE_TESTS") != "1", reason="wymaga izolowanego Docker PostgreSQL")]


@pytest.fixture
def client(db):
    db.start()
    app = create_app()
    app.state.database = db
    return TestClient(app)


def test_create_read_restart_and_order(client, db):
    assert client.get("/api/v1/projects").json() == {"items": []}
    first = client.post("/api/v1/projects", json={"name": " A ", "description": "  "})
    assert first.status_code == 201
    project = first.json()
    assert set(project) == {"id", "name", "description", "created_at"}
    assert project["name"] == "A" and project["description"] is None
    assert uuid.UUID(project["id"]).version == 4 and project["created_at"].endswith("Z")
    assert uuid.UUID(first.headers["X-Request-ID"]).version == 4
    second = client.post("/api/v1/projects", json={"name": "B", "description": " x "}).json()
    assert second["description"] == "x"
    same_time = datetime.now(timezone.utc)
    with db.session() as session:
        session.execute(text("UPDATE app.projects SET created_at=:created"), {"created": same_time})
    items = client.get("/api/v1/projects").json()["items"]
    assert [item["id"] for item in items] == sorted([project["id"], second["id"]])
    restarted = Database(None, {"blocked_capabilities": []})
    restarted.engine, restarted.sessions, restarted.startup_issue = db.engine, db.sessions, None
    restarted.start()
    client.app.state.database = restarted
    assert client.get("/api/v1/projects/" + project["id"]).json()["name"] == "A"


def test_conflicts_and_unicode(client):
    for first, second in [("Bank", " bank "), ("ŁÓDŹ", "łódź"), ("Straße", "STRASSE")]:
        assert client.post("/api/v1/projects", json={"name": first}).status_code == 201
        response = client.post("/api/v1/projects", json={"name": second})
        assert response.status_code == 409
        assert response.json()["error"]["details"]["fields"][0]["field"] == "name"
    for name in ["Lodz", "a  b", "a b", "é", "e\u0301", "x", "y" * 100]:
        assert client.post("/api/v1/projects", json={"name": name, "description": "z" * 2000}).status_code == 201


def test_parallel_unique_constraint(client, db):
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: client.post("/api/v1/projects", json={"name": "Parallel"}), range(2)))
    assert sorted(r.status_code for r in results) == [201, 409]
    with db.session() as session:
        assert session.execute(text("SELECT count(*) FROM app.projects")).scalar_one() == 1
    assert client.get("/api/v1/projects/" + next(r.json()["id"] for r in results if r.status_code == 201)).status_code == 200


def test_owner_isolation_and_global_conflict(client):
    project = client.post("/api/v1/projects", json={"name": "Shared"}).json()
    client.app.state.actor_context_provider = SimpleNamespace(get_context=lambda: ActorContext("other"))
    assert client.get("/api/v1/projects").json() == {"items": []}
    for identifier in (project["id"], str(uuid.uuid4())):
        response = client.get("/api/v1/projects/" + identifier)
        assert response.status_code == 404 and response.json()["error"]["details"]["fields"] == []
    assert client.post("/api/v1/projects", json={"name": "shared"}).status_code == 409


def test_database_constraints_and_rollback(client, db):
    with db.session() as session:
        assert session.execute(text("SELECT to_regclass('app.projects')")).scalar_one() == "projects"
    base = {"id": uuid.uuid4(), "owner": "owner", "name": "", "key": "test", "description": None}
    statement = text("INSERT INTO app.projects (id, owner_subject, name, name_key, description, created_at) VALUES (:id, :owner, :name, :key, :description, now())")
    for changes in ({}, {"name": "x" * 101}, {"name": "x", "description": "x" * 2001}, {"name": "x", "owner": None}):
        with pytest.raises(IntegrityError), db.session() as session:
            session.execute(statement, base | changes)
    with db.session() as session:
        assert session.execute(text("SELECT count(*) FROM app.projects")).scalar_one() == 0


def test_project_timestamps_are_utc_when_database_uses_other_timezone(client, db, postgres):
    from conftest import docker

    docker("exec", postgres[0], "psql", "-U", "postgres", "-d", "testdb", "-v", "ON_ERROR_STOP=1",
           "-c", "ALTER DATABASE testdb SET timezone TO 'Europe/Warsaw'")
    db.engine.dispose()
    try:
        with db.engine.connect() as connection:
            assert connection.execute(text("SHOW timezone")).scalar_one() == "Europe/Warsaw"
        created = client.post("/api/v1/projects", json={"name": "Strefa"})
        assert created.status_code == 201
        project = created.json()
        assert project["created_at"].endswith("Z")
        fetched = client.get("/api/v1/projects/" + project["id"])
        listed = client.get("/api/v1/projects")
        assert fetched.status_code == listed.status_code == 200
        assert fetched.json() == project
        assert listed.json()["items"] == [project]
    finally:
        db.engine.dispose()
        docker("exec", postgres[0], "psql", "-U", "postgres", "-d", "testdb", "-v", "ON_ERROR_STOP=1",
               "-c", "ALTER DATABASE testdb RESET timezone")
