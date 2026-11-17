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
    data = report("generation-service", [check("configuration")])
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
