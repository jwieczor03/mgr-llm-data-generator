"""Project API and its short-lived database operations."""
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, StrictStr, field_validator
from sqlalchemy import Column, DateTime, MetaData, Table, Text, Uuid, insert, select
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.exc import TimeoutError as DatabaseTimeout
from starlette.exceptions import HTTPException

from application_api.access import AccessDenied
from application_api.identity import ActorContextUnavailable

projects = Table(
    "projects", MetaData(),
    Column("id", Uuid, primary_key=True), Column("owner_subject", Text, nullable=False),
    Column("name", Text, nullable=False), Column("name_key", Text(collation="C"), nullable=False),
    Column("description", Text), Column("created_at", DateTime(timezone=True), nullable=False),
    schema="app",
)


class ProjectInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: StrictStr
    description: StrictStr | None = None

    @field_validator("name", "description")
    @classmethod
    def clean(cls, value, info):
        if value is None:
            return None
        value = value.strip()
        limit = 100 if info.field_name == "name" else 2000
        if "\x00" in value or len(value) > limit or (info.field_name == "name" and not value):
            raise ValueError("Nieprawidłowa wartość pola.")
        return value or None


class ProjectOutput(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def as_utc(cls, value):
        # PostgreSQL returns timestamptz in the session timezone, not necessarily UTC.
        return value.astimezone(timezone.utc)


class ProjectList(BaseModel):
    items: list[ProjectOutput]


class ProjectError(Exception):
    def __init__(self, status, code, message, fields=None):
        self.status, self.code, self.message, self.fields = status, code, message, fields or []


def error_response(request_id, status, code, message, fields=None):
    return JSONResponse(status_code=status, headers={"X-Request-ID": request_id}, content={
        "error": {"code": code, "message": message, "request_id": request_id,
                  "automatic_retry_allowed": False, "details": {"fields": fields or []}},
    })


class ProjectRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            request_id = str(uuid4())
            try:
                response = await original(request)
                response.headers["X-Request-ID"] = request_id
                return response
            except RequestValidationError as exc:
                fields = []
                for error in exc.errors():
                    loc = error["loc"]
                    field = "body" if error["type"] in ("json_invalid", "model_attributes_type") or len(loc) == 1 else str(loc[-1])
                    fields.append({"field": field, "message": "Nieprawidłowa wartość."})
                return error_response(request_id, 422, "VALIDATION_ERROR", "Nieprawidłowe dane żądania.", fields)
            except HTTPException as exc:
                # FastAPI wraps invalid JSON byte encoding in an HTTP 400 during parsing.
                if exc.status_code == 400 and isinstance(exc.__cause__, UnicodeDecodeError):
                    return error_response(request_id, 422, "VALIDATION_ERROR", "Nieprawidłowe dane żądania.",
                                          [{"field": "body", "message": "Nieprawidłowa wartość."}])
                return error_response(request_id, 500, "INTERNAL_ERROR", "Nie udało się wykonać operacji.")
            except ProjectError as exc:
                return error_response(request_id, exc.status, exc.code, exc.message, exc.fields)
            except ActorContextUnavailable:
                return error_response(request_id, 503, "actor_context_unavailable", "Brak kontekstu użytkownika.")
            except (OperationalError, DatabaseTimeout):
                return error_response(request_id, 503, "database_unavailable", "Baza danych jest niedostępna.")
            except DBAPIError as exc:
                if exc.connection_invalidated or getattr(exc.orig, "sqlstate", "") and str(exc.orig.sqlstate).startswith("08"):
                    return error_response(request_id, 503, "database_unavailable", "Baza danych jest niedostępna.")
                return error_response(request_id, 500, "INTERNAL_ERROR", "Nie udało się wykonać operacji.")
            except Exception:
                return error_response(request_id, 500, "INTERNAL_ERROR", "Nie udało się wykonać operacji.")

        return handler


router = APIRouter(prefix="/api/v1/projects", route_class=ProjectRoute)


def context(request):
    actor = request.app.state.actor_context_provider.get_context()
    if actor is None:
        raise ActorContextUnavailable()
    database = request.app.state.database
    if database.startup_issue == "configuration_missing":
        raise ProjectError(503, "configuration_unavailable", "Brak poprawnej konfiguracji bazy.")
    if database.report()["status"] != "ready":
        raise ProjectError(503, "database_unavailable", "Baza danych jest niedostępna.")
    return actor, database


@router.post("", status_code=201, response_model=ProjectOutput)
def create_project(data: ProjectInput, request: Request):
    actor, database = context(request)
    values = {"id": uuid4(), "owner_subject": actor.subject, "name": data.name,
              "name_key": data.name.casefold(), "description": data.description,
              "created_at": datetime.now(timezone.utc)}
    try:
        with database.session() as session:
            session.execute(insert(projects).values(**values))
    except IntegrityError as exc:
        # Only this named constraint represents the public name conflict.
        if (getattr(exc.orig, "sqlstate", None) == "23505" and
                getattr(getattr(exc.orig, "diag", None), "constraint_name", None) == "uq_projects_name_key"):
            raise ProjectError(409, "PROJECT_NAME_CONFLICT", "Nazwa projektu jest zajęta.",
                               [{"field": "name", "message": "Nazwa projektu jest zajęta."}]) from None
        raise
    return values


@router.get("", response_model=ProjectList)
def list_projects(request: Request):
    actor, database = context(request)
    with database.session() as session:
        rows = session.execute(select(projects).where(projects.c.owner_subject == actor.subject)
                               .order_by(projects.c.created_at.desc(), projects.c.id.asc())).mappings().all()
    return {"items": rows}


@router.get("/{project_id}", response_model=ProjectOutput)
def get_project(project_id: UUID, request: Request):
    actor, database = context(request)
    with database.session() as session:
        row = session.execute(select(projects).where(projects.c.id == project_id)).mappings().first()
        try:
            if row is None:
                raise AccessDenied()
            request.app.state.access_policy.require_owner(actor, row["owner_subject"])
        except AccessDenied:
            raise ProjectError(404, "PROJECT_NOT_FOUND", "Nie znaleziono projektu.") from None
    return row
