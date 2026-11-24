"""Private HTTP fixture with a controlled local Ollama-compatible server."""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import uvicorn
from generation_service.bootstrap import Settings, app, configure_llm


class OllamaHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers['Content-Length']))
        if self.path != '/api/chat':
            self.send_error(404)
            return
        data = json.dumps({'model': 'model', 'message': {'role': 'assistant', 'content': '{"relations":[]}'},
                           'done': True, 'done_reason': 'stop'}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), OllamaHandler)
threading.Thread(target=server.serve_forever, daemon=True).start()
app.state.settings = Settings(_env_file=None, llm_model='model', llm_context_tokens=20000,
    llm_output_tokens=100, llm_tokenizer_byte_bound_confirmed=True, llm_template_reserve_tokens=200,
    llm_backend='ollama', llm_base_url=f'http://127.0.0.1:{server.server_port}', llm_trusted_local='true')
app.state.llm_client_factory = configure_llm(app.state.settings)
uvicorn.run(app, host='127.0.0.1', port=int(sys.argv[1]), lifespan='off', log_level='critical')
server.shutdown()
