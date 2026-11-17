from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ActorContext:
    subject: str

    def __post_init__(self) -> None:
        if not isinstance(self.subject, str) or not self.subject.strip():
            raise ValueError("subject must be non-empty text")


class ActorContextUnavailable(Exception):
    """The trusted source could not provide an actor context."""


class ActorContextProvider(Protocol):
    def get_context(self) -> ActorContext | None: ...


LOCAL_OWNER_SUBJECT = "local-owner"


class LocalActorContextProvider:
    def get_context(self) -> ActorContext:
        return ActorContext(LOCAL_OWNER_SUBJECT)
