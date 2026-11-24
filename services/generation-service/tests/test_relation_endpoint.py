from fastapi.testclient import TestClient
from generation_service.bootstrap import Settings, app
from generation_service.llm import LlmClient, Response, Usage


class Transport:
    backend = 'fake'
    recipient = 'local'
    supported_options = frozenset()

    def __init__(self, trusted):
        self.trusted_local = trusted
        self.calls = 0

    async def send(self, call):
        self.calls += 1
        return Response('{"relations":[]}', Usage())


def test_private_endpoint_enforces_privacy_and_profile():
    payload = {'context': {'project_id': 'p', 'preparation_operation_id': 'op', 'schema_version_id': 'v',
                           'ddl_hash': 'hash', 'ddl': 'CREATE TABLE t(id int);', 'tables': []}}
    profile = Settings(_env_file=None, llm_model='model', llm_context_tokens=10000, llm_output_tokens=100,
                       llm_tokenizer_byte_bound_confirmed=True, llm_template_reserve_tokens=200)
    with TestClient(app) as client:
        app.state.settings = profile
        local = Transport(True)
        app.state.llm_client_factory = lambda: LlmClient(local)
        result = client.post('/internal/v1/relation-proposals', json=payload)
        assert result.status_code == 200 and result.json() == {'relations': []} and local.calls == 1
        external = Transport(False)
        app.state.llm_client_factory = lambda: LlmClient(external)
        result = client.post('/internal/v1/relation-proposals', json=payload)
        assert result.status_code == 422 and external.calls == 0
        result = client.post('/internal/v1/relation-proposals', json={'secret': 'never echo'})
        assert result.status_code == 422 and 'never echo' not in result.text
