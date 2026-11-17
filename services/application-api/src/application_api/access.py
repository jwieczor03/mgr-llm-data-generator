from typing import Protocol

from application_api.identity import ActorContext, ActorContextUnavailable


class AccessDenied(Exception):
    """The actor does not own the requested resource."""


class AccessPolicy(Protocol):
    def require_owner(self, actor: ActorContext | None, owner_subject: str | None) -> None: ...


class OwnershipAccessPolicy:
    def require_owner(self, actor: ActorContext | None, owner_subject: str | None) -> None:
        if actor is None:
            raise ActorContextUnavailable()
        if not isinstance(owner_subject, str) or not owner_subject.strip() or actor.subject != owner_subject:
            raise AccessDenied()
