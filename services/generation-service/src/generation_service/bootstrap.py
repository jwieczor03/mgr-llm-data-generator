from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Request
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from generation_service.interpretation import InterpretationService, Profile
from generation_service.llm import LlmClient
from generation_service.llm_transports import OllamaBackend, OpenAICompatibleBackend


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[2] / ".env", extra="ignore")
    llm_backend: str | None = None
    llm_base_url: str | None = None
    llm_api_key: str | None = Field(default=None, repr=False, exclude=True)
    llm_trusted_local: str | None = None


def configure_llm(settings: Settings) -> Callable[[], LlmClient] | None:
    fields = (settings.llm_backend, settings.llm_base_url, settings.llm_api_key, settings.llm_trusted_local)
    if all(value is None for value in fields):
        return None
    if not settings.llm_base_url or settings.llm_trusted_local not in (None, 'true', 'false'):
        raise ValueError('invalid configuration')
    if settings.llm_backend == 'ollama' and settings.llm_api_key is None:
        return partial(LlmClient, OllamaBackend(settings.llm_base_url,
            trusted_local_no_cloud_and_local_weights=settings.llm_trusted_local == 'true'))
    if settings.llm_backend == 'external' and settings.llm_trusted_local is None:
        return partial(LlmClient, OpenAICompatibleBackend(settings.llm_base_url, settings.llm_api_key or ''))
    raise ValueError('invalid configuration')


def create_interpretation_service(client_factory: Callable[[], LlmClient] | None,
                                  profile: Profile | None) -> InterpretationService:
    """Compose only an explicitly supplied, trusted model profile."""
    return InterpretationService(client_factory, profile)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.settings = Settings()
        app.state.llm_client_factory = None
        app.state.config_report = {"service": "generation-service", "status": "valid", "issues": [], "blocked_capabilities": []}
        try:
            app.state.llm_client_factory = configure_llm(app.state.settings)
        except ValueError:
            app.state.config_report = {"service": "generation-service", "status": "invalid",
                "issues": [{"field": "llm", "code": "invalid_llm_config", "message": "Konfiguracja LLM jest niepoprawna."}],
                "blocked_capabilities": ["llm"]}
    except (OSError, UnicodeError):
        app.state.settings = None
        app.state.llm_client_factory = None
        app.state.config_report = {"service": "generation-service", "status": "invalid", "issues": [{"field": None, "code": "config_unreadable", "message": "Nie można odczytać konfiguracji."}], "blocked_capabilities": []}
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/config")
def config(request: Request) -> dict:
    return request.app.state.config_report


@app.get("/health/ready")
def ready(request: Request) -> dict:
    valid = request.app.state.config_report["status"] == "valid"
    return {"service": "generation-service", "scope": "foundation",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "capacity": "capable" if valid else "incapable",
            "checks": [
                {"id": "process", "status": "ok", "code": "ok", "message": "Proces odpowiada.", "limitations": []},
                {"id": "configuration", "status": "ok" if valid else "failed",
                 "code": "ok" if valid else "configuration_unavailable",
                 "message": "Konfiguracja jest poprawna." if valid else "Konfiguracja jest niedostępna.", "limitations": []}],
            "limitations": ["Serwis jest szkieletem. Generowanie i walidacja danych nie są jeszcze zaimplementowane.",
                            "Nie sprawdzono dostawcy ani modelu LLM; nie wykonuje się płatnych prób."]}
