from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from application_api.config import load_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings, app.state.config_report = load_config()
    yield


FRONTEND_DIRECTORY = Path(__file__).resolve().parent / "web"


def live() -> dict[str, str]:
    return {"status": "ok"}


def config(request: Request) -> dict:
    return request.app.state.config_report


def create_app(frontend_directory: Path = FRONTEND_DIRECTORY) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_api_route("/health/live", live, methods=["GET"])
    app.add_api_route("/health/config", config, methods=["GET"])

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
