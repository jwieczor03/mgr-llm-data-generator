from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[2] / ".env", extra="ignore")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.settings = Settings()
        app.state.config_report = {"service": "generation-service", "status": "valid", "issues": [], "blocked_capabilities": []}
    except (OSError, UnicodeError):
        app.state.settings = None
        app.state.config_report = {"service": "generation-service", "status": "invalid", "issues": [{"field": None, "code": "config_unreadable", "message": "Nie można odczytać konfiguracji."}], "blocked_capabilities": []}
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/config")
def config(request: Request) -> dict:
    return request.app.state.config_report
