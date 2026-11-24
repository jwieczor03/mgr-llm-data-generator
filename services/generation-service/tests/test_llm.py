import asyncio
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from generation_service.llm import (
    Call,
    Identity,
    LlmClient,
    Message,
    PreflightError,
    TechnicalError,
    cost_subtotal,
    disclosure_hash,
)
from generation_service.llm_transports import OllamaBackend, OpenAICompatibleBackend


def run(coro):
    return asyncio.run(coro)


def call():
    return Call('operation', 'snapshot', Identity('single', '1'), Identity('prompt', '1'),
                'test-model', (Message('user', 'data'),), {}, 10, 100, 20,
                asyncio.get_running_loop().time() + 3)


@pytest.fixture
def server():
    requests = []
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            requests.append((self.path, body, dict(self.headers)))
            if body['model'] == 'slow':
                time.sleep(0.2)
            if body['model'] == 'failure':
                self.send_response(500)
                self.end_headers()
                return
            if self.path == '/api/chat':
                value = {'model': body['model'], 'message': {'role': 'assistant', 'content': 'ok'},
                         'done': True, 'done_reason': 'stop'}
            else:
                value = {'id': '1', 'object': 'chat.completion', 'created': 0, 'model': body['model'],
                         'choices': [{'index': 0, 'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': 'ok'}}]}
            if body['model'] == 'incomplete':
                if self.path == '/api/chat':
                    value.update(done_reason='length', prompt_eval_count=17, eval_count=4)
                else:
                    value['choices'][0]['finish_reason'] = 'length'
                    value['usage'] = {'prompt_tokens': 17, 'completion_tokens': 4, 'total_tokens': 21}
            data = json.dumps(value).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass
        def log_message(self, *_args):
            pass
    http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{http.server_port}', requests
    http.shutdown()
    http.server_close()
    thread.join()


def test_ollama_payload_measurements_no_cache(server):
    async def scenario():
        endpoint, requests = server
        client = LlmClient(OllamaBackend(endpoint, trusted_local_no_cloud_and_local_weights=True))
        first = call()
        assert (await client.complete(first)).text == 'ok'
        assert (await client.complete(first)).text == 'ok'
        assert len(requests) == 2
        assert client.attempts[0].actual_model == 'test-model'
        path, body, headers = requests[0]
        assert path == '/api/chat'
        assert body['truncate'] is False and body['shift'] is False
        assert body['messages'][0]['content'] == 'data'
        assert body['options']['num_predict'] == 20
        assert dict(client.attempts[0].options) == {'num_ctx': 100, 'num_predict': 20}
        assert 'authorization' not in {k.lower() for k in headers}
        assert all(a.usage.input_tokens is None and a.usage.cost is None for a in client.attempts)
        assert cost_subtotal(client.attempts, 'USD').partial
    run(scenario())


def test_external_gate_and_single_request_on_failure(server):
    async def scenario():
        endpoint, requests = server
        client = LlmClient(OpenAICompatibleBackend(endpoint + '/v1', 'fake-secret'))
        base = call()
        with pytest.raises(PreflightError):
            await client.complete(base)
        assert not requests and not client.attempts
        wrong_recipient = replace(base, disclosure_digest=disclosure_hash(base, endpoint + '/other'))
        with pytest.raises(PreflightError):
            await client.complete(wrong_recipient)
        approved = replace(base, disclosure_digest=disclosure_hash(base, client.transport.recipient))
        assert (await client.complete(approved)).text == 'ok'
        assert requests[0][1]['store'] is False
        assert dict(client.attempts[0].options) == {'max_completion_tokens': 20}
        assert 'fake-secret' not in repr(client.attempts)
        with pytest.raises(PreflightError):
            await client.complete(replace(approved, messages=(Message('user', 'changed'),)))
        failed = replace(approved, model='failure')
        with pytest.raises(TechnicalError):
            await client.complete(failed)
        assert len(requests) == 2
        assert client.attempts[-1].status == 'error'
    run(scenario())


def test_preflight_and_deadline_recording():
    class Slow:
        backend = 'fake'
        trusted_local = True
        supported_options = frozenset()
        async def send(self, _call):
            await asyncio.sleep(10)
    async def scenario():
        client = LlmClient(Slow())
        base = call()
        for bad in (replace(base, options={'unknown': 1}), replace(base, output_tokens=100)):
            with pytest.raises(PreflightError):
                await client.complete(bad)
        assert not client.attempts
        with pytest.raises(TimeoutError):
            await client.complete(replace(base, deadline=asyncio.get_running_loop().time() + 0.01))
        assert client.attempts[0].status == 'timeout'
        task = asyncio.create_task(client.complete(base))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert client.attempts[-1].status == 'cancelled'
    run(scenario())


def test_manual_strategy_switch_preserves_snapshot(server):
    from generation_service.llm import run_strategy

    class Strategy:
        def __init__(self, name, count):
            self.identity = Identity(name, '1')
            self.count = count

        async def run(self, execution):
            outputs = []
            for index in range(self.count):
                request = replace(call(), strategy=self.identity, prompt=Identity(f'prompt-{index}', '1'))
                outputs.append(await execution.complete(request))
            return outputs

    async def scenario():
        endpoint, requests = server
        client = LlmClient(OllamaBackend(endpoint, trusted_local_no_cloud_and_local_weights=True))
        await run_strategy(Strategy('single', 1), client, 'operation', 'snapshot')
        await run_strategy(Strategy('multi', 2), client, 'operation', 'snapshot')
        assert len(requests) == 3
        assert [a.strategy.name for a in client.attempts] == ['single', 'multi', 'multi']
        assert [a.prompt.name for a in client.attempts] == ['prompt-0', 'prompt-0', 'prompt-1']
        assert all(a.snapshot_hash == 'snapshot' and a.usage.cost is None for a in client.attempts)
        assert len({a.call_id for a in client.attempts}) == 3
    run(scenario())


@pytest.mark.parametrize('kind', ['ollama', 'external'])
def test_incomplete_preserves_available_usage(server, kind):
    async def scenario():
        endpoint, _ = server
        transport = (OllamaBackend(endpoint, trusted_local_no_cloud_and_local_weights=True)
                     if kind == 'ollama' else OpenAICompatibleBackend(endpoint + '/v1', 'fake-secret'))
        client = LlmClient(transport)
        request = replace(call(), model='incomplete')
        request = replace(request, disclosure_digest=disclosure_hash(request, client.transport.recipient))
        with pytest.raises(TechnicalError):
            await client.complete(request)
        usage = client.attempts[0].usage
        assert (usage.input_tokens, usage.output_tokens, usage.source) == (17, 4, 'provider')
        assert usage.total_tokens == (21 if kind == 'external' else None)
    run(scenario())


def test_late_response_is_discarded():
    from generation_service.llm import Response, Usage

    class SuppressesCancellation:
        backend = 'fake'
        trusted_local = True
        supported_options = frozenset()
        async def send(self, _call):
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                return Response('late', Usage())
    async def scenario():
        client = LlmClient(SuppressesCancellation())
        with pytest.raises(TimeoutError):
            await client.complete(replace(call(), deadline=asyncio.get_running_loop().time() + 0.01))
        assert client.attempts[0].status == 'timeout'
    run(scenario())


def test_cost_subtotal_marks_missing_and_currency():
    from decimal import Decimal

    from generation_service.llm import Attempt, Usage

    common = dict(operation_id='o', call_id='c', snapshot_hash='s', strategy=Identity('a', '1'),
                  prompt=Identity('p', '1'), backend='fake', model='m', actual_model='m',
                  options=(), elapsed_seconds=1, status='success')
    attempts = [Attempt(**common, usage=Usage(cost=Decimal('0.25'), currency='USD')),
                Attempt(**common, usage=Usage())]
    subtotal = cost_subtotal(attempts, 'USD')
    assert subtotal.value == Decimal('0.25') and subtotal.currency == 'USD' and subtotal.partial


def test_loopback_timeout_and_cancellation_after_request(server):
    async def scenario():
        endpoint, requests = server
        client = LlmClient(OllamaBackend(endpoint, trusted_local_no_cloud_and_local_weights=True))
        request = replace(call(), model='slow', deadline=asyncio.get_running_loop().time() + 0.08)
        with pytest.raises(TimeoutError):
            await client.complete(request)
        assert len(requests) == 1 and client.attempts[-1].status == 'timeout'
        request = replace(call(), model='slow')
        task = asyncio.create_task(client.complete(request))
        for _ in range(100):
            if len(requests) == 2:
                break
            await asyncio.sleep(0.005)
        assert len(requests) == 2
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert client.attempts[-1].status == 'cancelled'
    run(scenario())


def test_ambient_headers_cannot_override_explicit_configuration(server, monkeypatch):
    monkeypatch.setenv('OPENAI_CUSTOM_HEADERS', 'Authorization: Bearer ambient-secret\nX-Ambient: hidden\nContent-Type: text/plain')
    monkeypatch.setenv('OPENAI_ORG_ID', 'ambient-org')
    monkeypatch.setenv('OPENAI_PROJECT_ID', 'ambient-project')
    monkeypatch.setenv('OPENAI_ADMIN_KEY', 'ambient-admin')

    async def scenario():
        endpoint, requests = server
        client = LlmClient(OpenAICompatibleBackend(endpoint + '/v1', 'explicit-fake-key'))
        request = call()
        request = replace(request, disclosure_digest=disclosure_hash(request, client.transport.recipient))
        await client.complete(request)
        headers = {key.lower(): value for key, value in requests[0][2].items()}
        assert headers['authorization'] == 'Bearer explicit-fake-key'
        assert headers['content-type'] == 'application/json'
        assert not {'x-ambient', 'openai-organization', 'openai-project'} & headers.keys()
        assert 'ambient' not in repr(headers)
    run(scenario())


def test_debug_logging_in_fresh_process_does_not_expose_requests(server):
    endpoint, requests = server
    script = r"""
import asyncio, logging, sys
from dataclasses import replace
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('openai._base_client').addHandler(logging.StreamHandler())
logging.getLogger('httpcore.connection').addHandler(logging.StreamHandler())
from generation_service.llm import Call, Identity, LlmClient, Message, TechnicalError, disclosure_hash
from generation_service.llm_transports import OpenAICompatibleBackend
logging.getLogger('openai._base_client').setLevel(logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.DEBUG)
logging.getLogger('httpcore').setLevel(logging.DEBUG)
async def main():
    client = LlmClient(OpenAICompatibleBackend(sys.argv[1] + '/v1', 'KEY_SENTINEL'))
    for model in ('test-model', 'failure'):
        request = Call('operation', 'snapshot', Identity('s', '1'), Identity('p', '1'), model,
            (Message('user', 'PROMPT_SENTINEL'),), {}, 10, 100, 20, asyncio.get_running_loop().time() + 3)
        request = replace(request, disclosure_digest=disclosure_hash(request, client.transport.recipient))
        try:
            await client.complete(request)
        except TechnicalError:
            pass
    logging.getLogger('application').warning('APP_LOG_VISIBLE')
asyncio.run(main())
"""
    env = os.environ.copy()
    env.update(OPENAI_LOG='debug', OPENAI_CUSTOM_HEADERS='X-Private: AMBIENT_SENTINEL')
    process = subprocess.run([sys.executable, '-c', script, endpoint], env=env,
                             capture_output=True, text=True, timeout=15, check=True)
    output = process.stdout + process.stderr
    assert 'APP_LOG_VISIBLE' in output
    assert all(secret not in output for secret in ('PROMPT_SENTINEL', 'KEY_SENTINEL', 'AMBIENT_SENTINEL'))
    assert len(requests) == 2
