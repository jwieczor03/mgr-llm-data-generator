"""Provider-independent LLM boundary; no messages or credentials enter attempt records."""

import asyncio
import hashlib
import json
import math
import time
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class Identity:
    name: str
    version: str


@dataclass(frozen=True)
class Call:
    operation_id: str
    snapshot_hash: str
    strategy: Identity
    prompt: Identity
    model: str
    messages: tuple[Message, ...]
    options: dict[str, object]
    # A caller must supply a conservative count from a model-specific tokenizer.
    input_tokens_upper_bound: int
    max_context_tokens: int
    output_tokens: int
    deadline: float  # absolute asyncio loop time
    disclosure_digest: str | None = None


def disclosure_hash(call: Call, recipient: str) -> str:
    """Bind approval to the snapshot and every exact message sent to a provider."""
    data = [recipient, call.snapshot_hash, [[m.role, m.content] for m in call.messages]]
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Usage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cost: Decimal | None = None
    currency: str | None = None
    source: str | None = None


@dataclass(frozen=True)
class Response:
    text: str
    usage: Usage
    actual_model: str | None = None


@dataclass(frozen=True)
class Attempt:
    operation_id: str
    call_id: str
    snapshot_hash: str
    strategy: Identity
    prompt: Identity
    backend: str
    model: str
    actual_model: str | None
    options: tuple[tuple[str, object], ...]
    elapsed_seconds: float
    status: str
    usage: Usage


@dataclass(frozen=True)
class Subtotal:
    value: Decimal | None
    currency: str | None
    partial: bool


def cost_subtotal(attempts: list[Attempt], currency: str) -> Subtotal:
    costs = [a.usage.cost for a in attempts if a.usage.currency == currency and a.usage.cost is not None]
    return Subtotal(sum(costs, Decimal(0)) if costs else None, currency,
                    any(a.usage.cost is None or a.usage.currency != currency for a in attempts))


class PreflightError(ValueError):
    pass


class TechnicalError(Exception):
    def __init__(self, usage: Usage | None = None):
        super().__init__('LLM transport failed')
        self.usage = usage or Usage()


class Transport(Protocol):
    backend: str
    trusted_local: bool
    recipient: str
    supported_options: frozenset[str]

    async def send(self, call: Call) -> Response: ...


@dataclass
class LlmClient:
    transport: Transport
    attempts: list[Attempt] = field(default_factory=list)

    async def complete(self, call: Call) -> Response:
        if not all((call.operation_id, call.snapshot_hash, call.strategy.name, call.strategy.version,
                    call.prompt.name, call.prompt.version, call.model, call.messages)):
            raise PreflightError('missing identity or messages')
        if any(m.role not in {'system', 'user', 'assistant'} or not isinstance(m.content, str) for m in call.messages):
            raise PreflightError('invalid messages')
        if not set(call.options) <= self.transport.supported_options:
            raise PreflightError('unsupported option')
        if any(type(v) not in (float, int) or not math.isfinite(v) or not 0 <= v <= 2 for v in call.options.values()):
            raise PreflightError('invalid option')
        if (type(call.input_tokens_upper_bound) is not int or type(call.output_tokens) is not int
                or type(call.max_context_tokens) is not int or call.input_tokens_upper_bound < 0
                or call.output_tokens <= 0 or call.input_tokens_upper_bound + call.output_tokens > call.max_context_tokens):
            raise PreflightError('context budget exceeded or unavailable')
        if not self.transport.trusted_local and call.disclosure_digest != disclosure_hash(call, self.transport.recipient):
            raise PreflightError('disclosure approval missing or stale')
        remaining = call.deadline - asyncio.get_running_loop().time()
        if not math.isfinite(call.deadline) or remaining <= 0:
            raise PreflightError('deadline expired')
        model_options = dict(call.options)
        if self.transport.backend == 'ollama':
            model_options.update(num_ctx=call.max_context_tokens, num_predict=call.output_tokens)
        elif self.transport.backend == 'external_api':
            model_options['max_completion_tokens'] = call.output_tokens
        started = time.monotonic()
        status, usage, actual_model = 'error', Usage(), None
        try:
            async with asyncio.timeout_at(call.deadline):
                result = await self.transport.send(call)
            usage, actual_model = result.usage, result.actual_model
            if asyncio.current_task().cancelling():
                raise asyncio.CancelledError
            if asyncio.get_running_loop().time() >= call.deadline:
                raise TimeoutError
            status, usage, actual_model = 'success', result.usage, result.actual_model
            return result
        except TimeoutError:
            status = 'timeout'
            raise
        except asyncio.CancelledError:
            status = 'cancelled'
            raise
        except TechnicalError as exc:
            usage = exc.usage
            raise
        except Exception:
            # Provider exceptions may contain request bodies or keys.
            raise TechnicalError() from None
        finally:
            self.attempts.append(Attempt(call.operation_id, str(uuid.uuid4()), call.snapshot_hash,
                                         call.strategy, call.prompt, self.transport.backend, call.model, actual_model,
                                         tuple(sorted(model_options.items())), time.monotonic() - started,
                                         status, usage))


class Strategy(Protocol):
    identity: Identity

    async def run(self, execution: 'Execution') -> list[Response]: ...


@dataclass(frozen=True)
class Execution:
    """Composition fixes the operation, snapshot and strategy for all its calls."""
    client: LlmClient
    operation_id: str
    snapshot_hash: str
    strategy: Identity

    async def complete(self, call: Call) -> Response:
        if (call.operation_id, call.snapshot_hash, call.strategy) != (
                self.operation_id, self.snapshot_hash, self.strategy):
            raise PreflightError('execution identity mismatch')
        return await self.client.complete(call)


async def run_strategy(strategy: Strategy, client: LlmClient, operation_id: str, snapshot_hash: str) -> list[Response]:
    return await strategy.run(Execution(client, operation_id, snapshot_hash, strategy.identity))
