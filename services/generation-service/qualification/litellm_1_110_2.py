"""Reproduce LiteLLM's unlabelled estimate when Ollama omits one metric."""

import asyncio
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Avoid fetching the model cost map during the controlled local experiment.
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
os.environ['LITELLM_TELEMETRY'] = 'False'


class OllamaStub(BaseHTTPRequestHandler):
    requests: list[tuple[str, dict]] = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.requests.append((self.path, body))
        result = {
            'model': 'test',
            'message': {'role': 'assistant', 'content': 'ok'},
            'done': True,
            'prompt_eval_count': 17,
        }
        payload = json.dumps(result).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        pass


async def qualify(port: int) -> None:
    import litellm

    result = await litellm.acompletion(
        model='ollama_chat/test',
        api_base=f'http://127.0.0.1:{port}',
        messages=[{'role': 'user', 'content': 'x'}],
        extra_body={'truncate': False, 'shift': False},
        num_retries=0,
        timeout=5,
    )
    assert len(OllamaStub.requests) == 1
    path, body = OllamaStub.requests[0]
    assert path == '/api/chat'
    assert body['truncate'] is False and body['shift'] is False
    assert result.usage.prompt_tokens == 17
    # The stub supplied no eval_count. LiteLLM nevertheless returns a number.
    assert result.usage.completion_tokens == 1
    assert result.usage.total_tokens == 18
    print('Ollama: prompt_eval_count=17, eval_count absent')
    print('LiteLLM: prompt_tokens=17, completion_tokens=1, total_tokens=18')
    print('Request: /api/chat, truncate=false, shift=false; one request')


def main() -> None:
    OllamaStub.requests.clear()
    server = ThreadingHTTPServer(('127.0.0.1', 0), OllamaStub)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        asyncio.run(qualify(server.server_port))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    main()
