import asyncio
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import httpx
from application_api import bootstrap

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'monitor-service' / 'src'))
from monitor_service.diagnostics import probe as monitor_probe  # noqa: E402


class Database:
    def report(self):
        return {'issues': []}


class Artifacts:
    def report(self):
        return {'status': 'ready'}


def configured_app():
    app = bootstrap.create_app()
    app.state.settings = SimpleNamespace(generation_service_url='http://generation-service', validation_service_url='http://validation-service')
    app.state.config_report = {'status': 'valid'}
    app.state.database, app.state.artifacts = Database(), Artifacts()
    return app


def test_nested_slow_children_return_partial_to_monitor(monkeypatch):
    async def run():
        app = configured_app()
        client_class = httpx.AsyncClient
        original_probe = bootstrap.probe

        async def stalled(request):
            await asyncio.sleep(1)
            return httpx.Response(200, json={})

        async def short_probe(client, url, service):
            return await original_probe(client, url, service, total_timeout=0.05)

        async with client_class(transport=httpx.ASGITransport(app=app)) as outer:
            monkeypatch.setattr(bootstrap.httpx, 'AsyncClient', lambda **kwargs: client_class(transport=httpx.MockTransport(stalled), **kwargs))
            monkeypatch.setattr(bootstrap, 'probe', short_probe)
            result = await monitor_probe(outer, 'http://application-api', 'application-api', total_timeout=0.4)
        assert result['capacity'] == 'partial'
        checks = {item['id']: item['code'] for item in result['checks']}
        assert checks['database'] == checks['artifacts'] == 'ok'
        assert checks['generation'] == checks['validation'] == 'timeout'
    asyncio.run(run())


def test_slow_local_probe_only_times_out_that_dependency(monkeypatch):
    async def run():
        app = configured_app()
        app.state.database.report = lambda: (time.sleep(0.1), {'issues': []})[1]

        async def healthy(client, url, service):
            from application_api.diagnostics import check, report
            return report(service, [check('process'), check('configuration')])

        monkeypatch.setattr(bootstrap, 'probe', healthy)
        result = await bootstrap.ready_for_app(app, local_timeout=0.02)
        checks = {item['id']: item['code'] for item in result['checks']}
        assert checks['database'] == 'timeout'
        assert checks['artifacts'] == checks['generation'] == checks['validation'] == 'ok'
        assert result['capacity'] == 'partial'
    asyncio.run(run())


def test_backend_transport_rejects_incomplete_child_report():
    from application_api.diagnostics import check, probe, report

    async def run():
        child = report('generation-service', [check('configuration')])
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200, json=child))) as client:
            result = await probe(client, 'http://generation-service', 'generation-service')
            assert result['checks'][0]['code'] == 'invalid_report'
    asyncio.run(run())
