from dataclasses import FrozenInstanceError
from typing import Annotated

import pytest
from application_api.access import AccessDenied, AccessPolicy, OwnershipAccessPolicy
from application_api.bootstrap import (
    create_app,
    get_access_policy,
    require_actor_context,
)
from application_api.identity import (
    ActorContext,
    ActorContextUnavailable,
    LocalActorContextProvider,
)
from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient


@pytest.mark.parametrize("value", [None, 42, "", " \t\n"])
def test_subject_must_be_nonempty_text(value):
    with pytest.raises(ValueError):
        ActorContext(value)


def test_context_is_immutable_and_preserves_subject():
    actor = ActorContext(" owner ")
    assert actor.subject == " owner "
    with pytest.raises(FrozenInstanceError):
        actor.subject = "other"


def test_local_provider_is_stable():
    provider = LocalActorContextProvider()
    assert provider.get_context() == provider.get_context() == ActorContext("local-owner")


@pytest.mark.parametrize("owner", [None, "", " \t", "other", " local-owner", 123])
def test_policy_denies_non_owner(owner):
    with pytest.raises(AccessDenied):
        OwnershipAccessPolicy().require_owner(ActorContext("local-owner"), owner)


def test_policy_accepts_exact_owner_and_rejects_missing_actor():
    policy = OwnershipAccessPolicy()
    policy.require_owner(ActorContext("local-owner"), "local-owner")
    with pytest.raises(ActorContextUnavailable):
        policy.require_owner(None, "local-owner")


class Provider:
    def __init__(self, value):
        self.value = value

    def get_context(self):
        if isinstance(self.value, Exception):
            raise self.value
        return self.value


def app_with_test_route(provider=None, policy=None):
    app = create_app(actor_context_provider=provider, access_policy=policy)
    effects = []

    @app.post("/test-resource")
    def test_resource(
        actor: Annotated[ActorContext, Depends(require_actor_context)],
        access: Annotated[AccessPolicy, Depends(get_access_policy)],
    ):
        try:
            # In a real resource this comes from trusted persisted metadata.
            access.require_owner(actor, "local-owner")
        except AccessDenied:
            raise HTTPException(status_code=404, detail="not found") from None
        effects.append(actor.subject)
        return {"subject": actor.subject}

    return app, effects


def test_request_cannot_spoof_trusted_actor_or_owner():
    app, effects = app_with_test_route(Provider(ActorContext("other")))
    response = TestClient(app).post(
        "/test-resource?user_id=local-owner&owner=other",
        headers={"user-id": "local-owner", "owner": "other"},
        json={"user_id": "local-owner", "owner": "other"},
    )
    assert response.status_code == 404
    assert effects == []


@pytest.mark.parametrize("value", [None, ActorContextUnavailable("private provider details")])
def test_unavailable_context_is_safe_and_stops_handler(value):
    app, effects = app_with_test_route(Provider(value))
    response = TestClient(app).post("/test-resource")
    assert response.status_code == 503
    assert response.json() == {"detail": {"code": "actor_context_unavailable"}}
    assert effects == []
    assert TestClient(app).get("/health/live").json() == {"status": "ok"}


def test_instances_and_provider_are_independent():
    local, local_effects = app_with_test_route()
    foreign, foreign_effects = app_with_test_route(Provider(ActorContext("other")))
    assert TestClient(local).post("/test-resource").json() == {"subject": "local-owner"}
    assert TestClient(foreign).post("/test-resource").status_code == 404
    assert local_effects == ["local-owner"]
    assert foreign_effects == []
    assert local.state.access_policy is not foreign.state.access_policy
    assert local.state.actor_context_provider is not foreign.state.actor_context_provider


def test_policy_can_be_replaced():
    class DenyPolicy:
        def require_owner(self, actor, owner_subject):
            raise AccessDenied()

    app, effects = app_with_test_route(policy=DenyPolicy())
    assert TestClient(app).post("/test-resource").status_code == 404
    assert effects == []


def test_unexpected_provider_error_does_not_fall_back():
    app, effects = app_with_test_route(Provider(RuntimeError("provider failure")))
    response = TestClient(app, raise_server_exceptions=False).post("/test-resource")
    assert response.status_code == 500
    assert effects == []
