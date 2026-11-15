from pathlib import Path
from ipaddress import ip_address
import re
from urllib.parse import urlsplit

from fastapi import HTTPException, Request
from pydantic import SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore", hide_input_in_errors=True)

    app_db_host: str | None = None
    app_db_port: int | None = None
    app_db_name: str | None = None
    app_db_user: str | None = None
    app_db_password: SecretStr | None = None
    generation_service_url: str | None = None
    validation_service_url: str | None = None

    @field_validator("app_db_host")
    @classmethod
    def host_valid(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            ip_address(value)
        except ValueError:
            labels = value.split(".")
            if (len(value) > 253 or any(not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label) for label in labels)):
                raise ValueError("invalid host") from None
        return value

    @field_validator("app_db_port", mode="before")
    @classmethod
    def port_text_valid(cls, value):
        if value is not None and (not isinstance(value, str) or not value.isascii() or not value.isdigit()):
            raise ValueError("invalid port")
        return value

    @field_validator("app_db_port")
    @classmethod
    def port_valid(cls, value: int | None) -> int | None:
        if value is not None and not 1 <= value <= 65535:
            raise ValueError("invalid port")
        return value

    @field_validator("app_db_name", "app_db_user")
    @classmethod
    def text_valid(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("empty value")
        return value

    @field_validator("app_db_password")
    @classmethod
    def password_valid(cls, value: SecretStr | None) -> SecretStr | None:
        if value is not None and not value.get_secret_value():
            raise ValueError("empty value")
        return value

    @field_validator("generation_service_url", "validation_service_url")
    @classmethod
    def url_valid(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            url = urlsplit(value)
            port = url.port
            valid = (url.scheme in ("http", "https") and url.hostname and
                     url.username is None and url.password is None and url.path in ("", "/") and
                     not url.query and not url.fragment and not any(c.isspace() for c in value) and
                     (port is None or 1 <= port <= 65535))
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("invalid URL")
        return value


FIELDS = {
    "app_db_host": "database", "app_db_port": "database", "app_db_name": "database",
    "app_db_user": "database", "app_db_password": "database",
    "generation_service_url": "generation", "validation_service_url": "validation",
}


def load_config(env_file: Path = ENV_FILE) -> tuple[Settings | None, dict]:
    issues = []
    try:
        settings = Settings(_env_file=env_file)
    except ValidationError as exc:
        invalid = {str(error["loc"][0]) for error in exc.errors(include_input=False)}
        # Invalid fields are cleared before retaining independently valid values.
        issues.extend(
            {"field": name.upper(), "code": "invalid", "message": "Nieprawidłowa wartość."}
            for name in FIELDS if name in invalid
        )
        settings = Settings(_env_file=env_file, **{name: None for name in invalid})
    except (OSError, UnicodeError):
        return None, {"service": "application-api", "status": "invalid", "issues": [{"field": None, "code": "config_unreadable", "message": "Nie można odczytać konfiguracji."}], "blocked_capabilities": list(dict.fromkeys(FIELDS.values()))}

    invalid_fields = {issue["field"] for issue in issues}
    for name in FIELDS:
        if name.upper() not in invalid_fields and getattr(settings, name, None) is None:
            issues.append({"field": name.upper(), "code": "missing", "message": "Brak wymaganej wartości."})
    blocked = list(dict.fromkeys(FIELDS[issue["field"].lower()] for issue in issues))
    return settings, {"service": "application-api", "status": "invalid" if issues else "valid", "issues": issues, "blocked_capabilities": blocked}


def require_capabilities(*capabilities: str):
    def dependency(request: Request) -> None:
        blocked = [item for item in capabilities if item in request.app.state.config_report["blocked_capabilities"]]
        if blocked:
            raise HTTPException(status_code=503, detail={"code": "configuration_unavailable", "blocked_capabilities": blocked})
    return dependency
