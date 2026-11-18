import uuid
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from application_api.bootstrap import create_app
from application_api.identity import ActorContextUnavailable
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, OperationalError


class FakeDatabase:
    startup_issue = None

    def report(self):
        return {"status": "ready"}

    @contextmanager
    def session(self):
        raise RuntimeError("secret SQL SELECT")
        yield


@pytest.fixture
def client():
    app = create_app()
    app.state.database = FakeDatabase()
    return TestClient(app)


def assert_error(response, status, code, field=None):
    assert response.status_code == status
    error = response.json()["error"]
    assert error["code"] == code
    assert error["automatic_retry_allowed"] is False
    assert str(uuid.UUID(error["request_id"], version=4)) == error["request_id"]
    assert response.headers["X-Request-ID"] == error["request_id"]
    assert [item["field"] for item in error["details"]["fields"]] == ([] if field is None else [field])
    assert "secret" not in response.text and "SELECT" not in response.text


@pytest.mark.parametrize("payload,field", [
    ({}, "name"), ({"name": None}, "name"), ({"name": 3}, "name"),
    ({"name": True}, "name"), ({"name": " "}, "name"), ({"name": "a" * 101}, "name"),
    ({"name": "a\x00"}, "name"), ({"name": "a", "description": "a" * 2001}, "description"),
    ({"name": "a", "description": "\x00"}, "description"),
    ({"name": "a", "description": False}, "description"),
    ({"name": "a", "owner_subject": "other"}, "owner_subject"),
    ({"name": "a", "extra": 1}, "extra"),
    ([], "body"), (None, "body"),
])
def test_invalid_payload(client, payload, field):
    assert_error(client.post("/api/v1/projects", json=payload), 422, "VALIDATION_ERROR", field)


def test_invalid_json_and_uuid(client):
    assert_error(client.post("/api/v1/projects", content="{", headers={"Content-Type": "application/json"}), 422, "VALIDATION_ERROR", "body")
    assert_error(client.get("/api/v1/projects/secret"), 422, "VALIDATION_ERROR", "project_id")


def test_request_id_is_generated_and_unexpected_error_is_safe(client):
    response = client.post("/api/v1/projects", json={"name": "a"}, headers={"X-Request-ID": "client-id"})
    assert_error(response, 500, "INTERNAL_ERROR")
    assert response.headers["X-Request-ID"] != "client-id"


def test_unavailable_dependencies(client):
    class MissingActor:
        def get_context(self):
            raise ActorContextUnavailable()
    client.app.state.actor_context_provider = MissingActor()
    assert_error(client.get("/api/v1/projects"), 503, "actor_context_unavailable")
    client.app.state.actor_context_provider = SimpleNamespace(get_context=lambda: SimpleNamespace(subject="one"))
    client.app.state.database.startup_issue = "configuration_missing"
    assert_error(client.get("/api/v1/projects"), 503, "configuration_unavailable")
    client.app.state.database.startup_issue = "migration_failed"
    client.app.state.database.report = lambda: {"status": "unavailable"}
    assert_error(client.get("/api/v1/projects"), 503, "database_unavailable")


def test_database_errors_do_not_leak_or_fake_conflict(client):
    @contextmanager
    def fail(exc):
        raise exc
        yield
    client.app.state.database.session = lambda: fail(OperationalError("secret SELECT", {}, Exception("secret")))
    assert_error(client.post("/api/v1/projects", json={"name": "a"}), 503, "database_unavailable")
    client.app.state.database.session = lambda: fail(IntegrityError("secret SELECT", {}, Exception("secret")))
    assert_error(client.post("/api/v1/projects", json={"name": "a"}), 500, "INTERNAL_ERROR")
