import asyncio
import json

import httpx
from fastapi.testclient import TestClient
from monitor_service.bootstrap import Monitor, Settings, create_app
from monitor_service.diagnostics import capacity, check, clean_report, probe, report


def test_capacity():
    assert capacity([check("configuration")]) == "capable"
    assert capacity([check("configuration", "unreachable")]) == "incapable"
    assert capacity([check("configuration"), check("database", "connection_failed")]) == "partial"


def test_untrusted_strings_never_pass_through():
    data = report("generation-service", [check("process"), check("configuration")])
    data["checks"][0]["message"] = "SECRET"
    data["limitations"] = ["SECRET"]
    assert "SECRET" not in json.dumps(clean_report(data, "generation-service"))


def test_transport_rejects_redirect_large_and_invalid():
    async def run():
        for response, expected in [(httpx.Response(302, headers={"Location": "http://bad/"}), "http_error"),
                                   (httpx.Response(200, content=b"x" * 65537), "invalid_report"),
                                   (httpx.Response(200, json={"secret": "SECRET"}), "invalid_report")]:
            async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: response)) as client:
                result = await probe(client, "http://backend", "generation-service")
                assert result["checks"][0]["code"] == expected
                assert "SECRET" not in json.dumps(result)
    asyncio.run(run())


def test_scheduler_single_flight_and_manual_does_not_move_deadline():
    async def run():
        monitor = Monitor(Settings(_env_file=None), interval=1800, clock=lambda: 100)
        deadline = monitor.next_deadline
        assert monitor.start_run()
        assert monitor.start_run() is None
        assert monitor.next_deadline == deadline
        await monitor.close()
    asyncio.run(run())


def test_panel_access_and_request_security():
    app = create_app(Settings(_env_file=None, application_api_url="", generation_service_url="", validation_service_url=""), hosts=["testserver"])
    with TestClient(app) as client:
        assert client.get('/health/live').json() == {"status": "ok"}
        assert client.post('/api/v1/check').status_code == 403
        assert client.post('/api/v1/check', headers={"X-Monitor-Request": "1", "Origin": "http://evil"}).status_code == 403
        assert client.get('/api/v1/report').json()["scope"] == "foundation"
        assert client.get('/health/live', headers={"Host": "evil"}).status_code == 400


def test_periodic_collision_runs_once_after_manual(monkeypatch):
    async def run():
        import monitor_service.bootstrap as bootstrap

        started = asyncio.Event()
        release = asyncio.Event()
        calls = []

        async def controlled_probe(client, url, name):
            calls.append(name)
            started.set()
            await release.wait()
            return report(name, [check("configuration")])

        monkeypatch.setattr(bootstrap, "probe", controlled_probe)
        monitor = Monitor(Settings(_env_file=None), interval=0.05)
        first_deadline = monitor.next_deadline
        monitor.start_run()
        monitor.scheduler = asyncio.create_task(monitor.schedule())
        await started.wait()
        await asyncio.sleep(0.07)
        assert monitor.pending
        assert monitor.start_run() is None
        assert monitor.next_deadline > first_deadline
        release.set()
        for _ in range(100):
            if len(calls) >= 6 and monitor.active.done():
                break
            await asyncio.sleep(0.002)
        assert len(calls) == 6
        assert monitor.current()["capacity"] == "capable"
        await monitor.close()
    asyncio.run(run())


def test_not_checked_stale_and_fresh_failure():
    from datetime import datetime, timedelta, timezone

    async def run():
        monitor = Monitor(Settings(_env_file=None))
        assert monitor.current()["freshness"] == "not_checked"
        failed = report("application-api", [check("configuration", "unreachable")])
        monitor.snapshot = {"checked_at": datetime.now(timezone.utc).isoformat(), "capacity": "incapable", "services": [failed]}
        assert monitor.current()["freshness"] == "fresh"
        monitor.snapshot["checked_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1831)).isoformat()
        assert monitor.current()["freshness"] == "stale"
        await monitor.close()
    asyncio.run(run())


def test_invalid_url_does_not_hide_other_services():
    async def run():
        settings = Settings(_env_file=None, application_api_url='http://\u00a0bad')
        monitor = Monitor(settings)
        await monitor.client.aclose()
        monitor.client = httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=report(request.url.host, [check('process'), check('configuration')]))))
        await monitor.run()
        items = {item['service']: item for item in monitor.snapshot['services']}
        assert items['application-api']['checks'][0]['code'] == 'configuration_unavailable'
        assert items['generation-service']['capacity'] == 'capable'
        assert items['validation-service']['capacity'] == 'capable'
        await monitor.close()
    asyncio.run(run())


def test_incomplete_duplicate_and_wrong_catalog_are_invalid():
    async def run():
        api = [check(name) for name in ('process', 'configuration', 'database', 'artifacts', 'generation', 'validation')]
        cases = [api[:-1], api + [check('database')], [check('process'), check('configuration'), check('database')]]
        for checks in cases:
            async with httpx.AsyncClient(transport=httpx.MockTransport(
                    lambda _: httpx.Response(200, json=report('application-api', checks)))) as client:
                result = await probe(client, 'http://application-api', 'application-api')
                assert result['checks'][0]['code'] == 'invalid_report'
    asyncio.run(run())


def test_api_read_timeout_over_real_socket_exceeds_five_seconds():
    async def run():
        payload = json.dumps(report('application-api', [check(name) for name in
            ('process', 'configuration', 'database', 'artifacts', 'generation', 'validation')])).encode()

        async def serve(reader, writer):
            await reader.readuntil(b'\r\n\r\n')
            writer.write(f'HTTP/1.1 200 OK\r\nContent-Length: {len(payload)}\r\n\r\n'.encode())
            await writer.drain()
            await asyncio.sleep(5.2)
            writer.write(payload)
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        server = await asyncio.start_server(serve, '127.0.0.1', 0)
        port = server.sockets[0].getsockname()[1]
        try:
            async with httpx.AsyncClient(trust_env=False, timeout=httpx.Timeout(5, connect=2)) as client:
                result = await probe(client, f'http://127.0.0.1:{port}', 'application-api')
            assert result['capacity'] == 'capable'
        finally:
            server.close()
            await server.wait_closed()
    asyncio.run(run())


def test_request_timeouts_differ_by_target():
    async def run():
        async def handler(request):
            timeout = request.extensions['timeout']
            assert timeout['connect'] == 2
            assert timeout['read'] == (10 if request.url.host == 'application-api' else 5)
            names = (('process', 'configuration', 'database', 'artifacts', 'generation', 'validation')
                     if request.url.host == 'application-api' else ('process', 'configuration'))
            return httpx.Response(200, json=report(request.url.host, [check(name) for name in names]))

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            for service in ('application-api', 'generation-service', 'validation-service'):
                assert (await probe(client, 'http://' + service, service))['capacity'] == 'capable'
    asyncio.run(run())


def test_failed_process_and_unexpected_probe_exception_are_isolated():
    async def run():
        broken = report('generation-service', [check('process', 'timeout'), check('configuration')])
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200, json=broken))) as client:
            assert (await probe(client, 'http://generation-service', 'generation-service'))['checks'][0]['code'] == 'invalid_report'

        def unexpected(_):
            raise RuntimeError('secret exception')

        async with httpx.AsyncClient(transport=httpx.MockTransport(unexpected)) as client:
            result = await probe(client, 'http://generation-service', 'generation-service')
            assert result['checks'][0]['code'] == 'diagnostic_failed'
            assert 'secret exception' not in json.dumps(result)
    asyncio.run(run())
