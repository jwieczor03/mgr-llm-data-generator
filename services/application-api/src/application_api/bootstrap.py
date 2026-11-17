import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from application_api.access import AccessPolicy, OwnershipAccessPolicy
from application_api.artifact_store import LocalArtifactStore, UnconfiguredArtifactStore
from application_api.config import load_config
from application_api.database import Database
from application_api.diagnostics import check, probe, report
from application_api.identity import (
    ActorContext,
    ActorContextProvider,
    ActorContextUnavailable,
    LocalActorContextProvider,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings, app.state.config_report = load_config()
    app.state.artifacts = (UnconfiguredArtifactStore() if app.state.settings is None or "artifacts" in app.state.config_report["blocked_capabilities"]
                           else LocalArtifactStore(app.state.settings.artifact_project_root, app.state.settings.artifact_working_root))
    app.state.database = Database(app.state.settings, app.state.config_report)
    await run_in_threadpool(app.state.database.start)
    try:
        await ready_for_app(app)
    except Exception:
        pass  # Startup diagnostics must not prevent the diagnostic server from starting.
    try:
        yield
    finally:
        await run_in_threadpool(app.state.database.close)


FRONTEND_DIRECTORY = Path(__file__).resolve().parent / "web"


def live() -> dict[str, str]:
    return {"status": "ok"}


def config(request: Request) -> dict:
    return request.app.state.config_report


def database_health(request: Request) -> dict:
    return request.app.state.database.report()


def artifacts_health(request: Request) -> dict:
    return request.app.state.artifacts.report()


async def ready_for_app(app: FastAPI) -> dict:
    config = app.state.config_report
    settings = app.state.settings
    checks = [check("process"), check("configuration", "ok" if config["status"] == "valid" else "configuration_unavailable")]
    database, artifacts = await asyncio.gather(
        run_in_threadpool(app.state.database.report), run_in_threadpool(app.state.artifacts.report))
    db_code = database["issues"][0]["code"] if database["issues"] else "ok"
    checks.append(check("database", db_code))
    if artifacts["status"] == "ready":
        artifact_code = "ok"
    else:
        artifact_code = next((artifacts[n]["code"] for n in ("project", "working") if artifacts[n]["code"]), "diagnostic_failed")
    checks.append(check("artifacts", artifact_code))
    async with httpx.AsyncClient(timeout=httpx.Timeout(5, connect=2), follow_redirects=False, trust_env=False) as client:
        children = await asyncio.gather(*(
            probe(client, getattr(settings, name + "_service_url", None) if settings else None, name + "-service")
            for name in ("generation", "validation")))
    for name, child in zip(("generation", "validation"), children):
        if child["capacity"] == "capable":
            checks.append(check(name))
        else:
            failed = next((c for c in child["checks"] if c["status"] != "ok"), None)
            checks.append(check(name, failed["code"] if failed else "diagnostic_failed"))
    return report("application-api", checks)


async def ready(request: Request) -> dict:
    return await ready_for_app(request.app)


def require_actor_context(request: Request) -> ActorContext:
    try:
        actor = request.app.state.actor_context_provider.get_context()
        if actor is None:
            raise ActorContextUnavailable()
        return actor
    except ActorContextUnavailable:
        raise HTTPException(status_code=503, detail={"code": "actor_context_unavailable"}) from None


def get_access_policy(request: Request) -> AccessPolicy:
    return request.app.state.access_policy


def create_app(
    frontend_directory: Path = FRONTEND_DIRECTORY,
    *,
    actor_context_provider: ActorContextProvider | None = None,
    access_policy: AccessPolicy | None = None,
) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.state.actor_context_provider = (LocalActorContextProvider() if actor_context_provider is None
                                        else actor_context_provider)
    app.state.access_policy = OwnershipAccessPolicy() if access_policy is None else access_policy
    app.add_api_route("/health/live", live, methods=["GET"])
    app.add_api_route("/health/ready", ready, methods=["GET"])
    app.add_api_route("/health/config", config, methods=["GET"])
    app.add_api_route("/health/database", database_health, methods=["GET"])
    app.add_api_route("/health/artifacts", artifacts_health, methods=["GET"])

    # Missing build output must not prevent configuration diagnostics from starting.
    if (frontend_directory / "index.html").is_file():
        @app.get("/", include_in_schema=False)
        def index() -> FileResponse:
            return FileResponse(frontend_directory / "index.html")

        # Mount only build assets, so unknown API and page paths remain JSON 404s.
        if (frontend_directory / "assets").is_dir():
            app.mount("/assets", StaticFiles(directory=frontend_directory / "assets"), name="assets")

    return app


app = create_app()
