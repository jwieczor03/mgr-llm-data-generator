"""SDK transports configured for one request, without retries or ambient proxies."""

import ipaddress
import json
from urllib.parse import urlsplit

import httpx
from ollama import AsyncClient
from openai import AsyncOpenAI

from generation_service.llm import Call, Response, TechnicalError, Usage


def _endpoint(url: str, *, ollama: bool = False) -> str:
    parts = urlsplit(url)
    if parts.scheme not in {'http', 'https'} or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError('invalid endpoint')
    try:
        port = parts.port
    except ValueError:
        raise ValueError('invalid endpoint') from None
    try:
        loopback = ipaddress.ip_address(parts.hostname).is_loopback
    except ValueError:
        loopback = False
    if port is not None and not 1 <= port <= 65535:
        raise ValueError('invalid endpoint')
    if not ollama and parts.scheme == 'http' and not loopback:
        raise ValueError('HTTPS required')
    if ollama and parts.path not in ('', '/'):
        raise ValueError('invalid Ollama path')
    return url.rstrip('/')


class _OllamaTransport(httpx.AsyncBaseTransport):
    def __init__(self, endpoint: str):
        self.endpoint = httpx.URL(endpoint)
        self.delegate = httpx.AsyncHTTPTransport(retries=0, trust_env=False)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        expected = self.endpoint.copy_with(path='/api/chat')
        if request.method != 'POST' or request.url != expected:
            raise ValueError('unexpected Ollama request')
        body = json.loads(request.content)
        body.update(truncate=False, shift=False)
        headers = request.headers.copy()
        headers.pop('authorization', None)
        payload = json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode()
        headers['content-length'] = str(len(payload))
        clean = httpx.Request('POST', request.url, headers=headers, content=payload)
        return await self.delegate.handle_async_request(clean)

    async def aclose(self) -> None:
        await self.delegate.aclose()


class OllamaBackend:
    backend = 'ollama'
    supported_options = frozenset({'temperature'})

    def __init__(self, endpoint: str, *, trusted_local_no_cloud_and_local_weights: bool = False):
        self.endpoint = _endpoint(endpoint, ollama=True)
        self.recipient = self.endpoint
        self.trusted_local = trusted_local_no_cloud_and_local_weights is True

    async def send(self, call: Call) -> Response:
        transport = _OllamaTransport(self.endpoint)
        client = AsyncClient(host=self.endpoint, transport=transport, trust_env=False, follow_redirects=False, timeout=None)
        try:
            result = await client.chat(model=call.model,
                messages=[{'role': m.role, 'content': m.content} for m in call.messages],
                stream=False, options={'num_ctx': call.max_context_tokens, 'num_predict': call.output_tokens, **call.options})
            usage = Usage(input_tokens=result.prompt_eval_count, output_tokens=result.eval_count,
                          source='provider' if result.prompt_eval_count is not None or result.eval_count is not None else None)
            if not result.done or result.done_reason not in ('stop', None):
                raise TechnicalError(usage)
            return Response(result.message.content or '', usage, result.model)
        finally:
            await client.close()


class OpenAICompatibleBackend:
    backend = 'external_api'
    trusted_local = False
    supported_options = frozenset({'temperature'})

    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = _endpoint(endpoint)
        self.recipient = self.endpoint
        if not api_key or not api_key.strip():
            raise ValueError('missing credential')
        self._api_key = api_key

    async def send(self, call: Call) -> Response:
        async with httpx.AsyncClient(trust_env=False, follow_redirects=False, timeout=None) as http:
            async with AsyncOpenAI(base_url=self.endpoint, api_key=self._api_key, max_retries=0, timeout=None, http_client=http) as client:
                result = await client.chat.completions.create(
                    model=call.model, messages=[{'role': m.role, 'content': m.content} for m in call.messages],
                    stream=False, store=False, max_completion_tokens=call.output_tokens, **call.options)
                raw = result.usage
                usage = Usage(input_tokens=raw.prompt_tokens if raw else None,
                              output_tokens=raw.completion_tokens if raw else None,
                              total_tokens=raw.total_tokens if raw else None,
                              source='provider' if raw else None)
                if len(result.choices) != 1 or result.choices[0].finish_reason != 'stop':
                    raise TechnicalError(usage)
                return Response(result.choices[0].message.content or '', usage, result.model)
