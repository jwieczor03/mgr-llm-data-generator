"""Independent local monitor; diagnostics never perform business operations."""
import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.middleware.trustedhost import TrustedHostMiddleware

from monitor_service.diagnostics import LIMITATIONS, check, probe, report


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[2] / ".env", extra="ignore")
    application_api_url: str = "http://application-api:8000"
    generation_service_url: str = "http://generation-service:8000"
    validation_service_url: str = "http://validation-service:8000"


class Monitor:
    def __init__(self, settings, *, interval=1800, clock=time.monotonic):
        self.settings, self.interval, self.clock = settings, interval, clock
        self.origin = clock()
        self.next_deadline = self.origin + interval
        self.snapshot = None
        self.run_id = None
        self.active = None
        self.scheduler = None
        self.pending = False
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(5, connect=2), follow_redirects=False, trust_env=False)

    def start_run(self):
        if self.active and not self.active.done():
            return None
        self.run_id = str(uuid.uuid4())
        self.active = asyncio.create_task(self.run())
        return self.run_id

    async def run(self):
        names = ("application-api", "generation-service", "validation-service")
        urls = (self.settings.application_api_url, self.settings.generation_service_url, self.settings.validation_service_url)
        try:
            async with asyncio.timeout(30):
                results = await asyncio.gather(*(probe(self.client, url, name) for url, name in zip(urls, names)))
        except Exception:
            results = [report(name, [check("configuration", "diagnostic_failed")]) for name in names]
        statuses = [item["capacity"] for item in results]
        overall = "capable" if all(s == "capable" for s in statuses) else (
            "incapable" if all(s == "incapable" for s in statuses) else "partial")
        self.snapshot = {"checked_at": datetime.now(timezone.utc).isoformat(), "capacity": overall, "services": results}
        self.run_id = None
        if self.pending:
            self.pending = False
            # Run after this task has returned so the single-flight guard sees it completed.
            asyncio.get_running_loop().call_soon(self.start_run)

    async def schedule(self):
        while True:
            await asyncio.sleep(max(0, self.next_deadline - self.clock()))
            while self.next_deadline <= self.clock():
                self.next_deadline += self.interval
            if self.active and not self.active.done():
                self.pending = True
            else:
                self.start_run()

    def current(self):
        snapshot = self.snapshot or {"checked_at": None, "capacity": None, "services": []}
        checked = snapshot["checked_at"]
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(checked)).total_seconds() if checked else None
        limitations = LIMITATIONS.copy()
        if self.scheduler and self.scheduler.done():
            limitations.append("Harmonogram monitora nie działa. Uruchom monitor ponownie.")
        return {"scope": "foundation", **snapshot,
                "freshness": "not_checked" if age is None else "stale" if age > 1830 else "fresh",
                "in_progress": bool(self.active and not self.active.done()), "run_id": self.run_id,
                "next_automatic_at": (datetime.now(timezone.utc) + timedelta(seconds=max(0, self.next_deadline - self.clock()))).isoformat(),
                "limitations": limitations}

    async def close(self):
        for task in (self.scheduler, self.active):
            if task and not task.done():
                task.cancel()
        await asyncio.gather(*(t for t in (self.scheduler, self.active) if t), return_exceptions=True)
        await self.client.aclose()


def create_app(settings=None, *, hosts=None, frontend=None):
    @asynccontextmanager
    async def lifespan(app):
        try:
            configuration = settings or Settings()
        except (OSError, UnicodeError, ValueError):
            configuration = Settings(_env_file=None, application_api_url="", generation_service_url="", validation_service_url="")
        app.state.monitor = Monitor(configuration)
        app.state.monitor.start_run()
        app.state.monitor.scheduler = asyncio.create_task(app.state.monitor.schedule())
        yield
        await app.state.monitor.close()

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts or ["localhost", "127.0.0.1", "monitor-service"])

    @app.middleware("http")
    async def security(request, call_next):
        origin = request.headers.get("origin")
        if request.method == "POST" and (request.headers.get("x-monitor-request") != "1" or
                (origin is not None and origin != f"{request.url.scheme}://{request.headers.get('host')}")):
            response = JSONResponse({"code": "forbidden"}, status_code=403)
        else:
            response = await call_next(request)
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'"})
        return response

    @app.get("/health/live")
    def live():
        return {"status": "ok"}

    @app.get("/api/v1/report")
    def get_report(request: Request):
        return request.app.state.monitor.current()

    @app.post("/api/v1/check")
    async def start_check(request: Request):
        monitor = request.app.state.monitor
        run_id = monitor.start_run()
        if run_id is None:
            return JSONResponse({"code": "check_in_progress", "run_id": monitor.run_id}, status_code=409)
        return JSONResponse({"run_id": run_id, "status": "running"}, status_code=202)

    frontend = frontend or Path(__file__).resolve().parent / "web"
    if (frontend / "index.html").is_file():
        @app.get("/", include_in_schema=False)
        def index():
            return FileResponse(frontend / "index.html")
        if (frontend / "assets").is_dir():
            app.mount("/assets", StaticFiles(directory=frontend / "assets"), name="assets")
    return app


app = create_app()
