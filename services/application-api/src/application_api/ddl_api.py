"""Public API for the DDL upload protocol."""
import json
from uuid import UUID, uuid4

from fastapi import APIRouter, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRoute
from pydantic import UUID4, BaseModel, ConfigDict, Field, StrictInt, StrictStr
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.exc import TimeoutError as DatabaseTimeout
from starlette.concurrency import run_in_threadpool

from application_api.access import AccessDenied
from application_api.artifact_store import ArtifactRef
from application_api.ddl_input import (
    InputError,
    receive_multipart,
    validate_content,
    validate_metadata,
)
from application_api.ddl_repository import DdlRepository, sha256
from application_api.ddl_runtime import io_lock
from application_api.identity import ActorContextUnavailable
from application_api.projects import ProjectError, context


class DdlRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            request_id = str(uuid4())
            try:
                response = await original(request)
                response.headers["X-Request-ID"] = request_id
                return response
            except RequestValidationError:
                status, code, details = 422, "VALIDATION_ERROR", {}
            except InputError as exc:
                code, details = exc.code, exc.details or {}
                if code == "DDL_UPLOAD_ALREADY_RECEIVED":
                    details = {"status_url": request.url.path.removesuffix("/files")}
                status = (404 if code == "DDL_ATTEMPT_NOT_FOUND" else 413 if code == "DDL_LIMIT_EXCEEDED"
                          else 422 if code in ("VALIDATION_ERROR", "DDL_INPUT_INVALID") else 409)
            except ProjectError as exc:
                status, code, details = exc.status, exc.code, {}
            except ActorContextUnavailable:
                status, code, details = 503, "actor_context_unavailable", {}
            except (OperationalError, DatabaseTimeout):
                status, code, details = 503, "database_unavailable", {}
            except DBAPIError as exc:
                status = 503 if exc.connection_invalidated or str(getattr(exc.orig, "sqlstate", "")).startswith("08") else 500
                code, details = ("database_unavailable" if status == 503 else "INTERNAL_ERROR"), {}
            except Exception:
                status, code, details = 500, "INTERNAL_ERROR", {}
            return JSONResponse(status_code=status, headers={"X-Request-ID": request_id}, content={"error": {
                "code": code, "message": "Nie udało się wykonać operacji DDL.", "request_id": request_id,
                "automatic_retry_allowed": False, "details": details}})
        return handler


class FileMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: StrictStr
    size_bytes: StrictInt = Field(ge=0)


class Reservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page_id: UUID4
    files: list[FileMetadata]


class Page(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page_id: UUID4


class Receipt(Page):
    receipt_nonce: StrictStr


router = APIRouter(prefix="/api/v1/projects/{project_id}", route_class=DdlRoute)


def access(request, project_id):
    actor, database = context(request)
    if getattr(request.app.state, "ddl_settings", None) is None or getattr(request.app.state, "ddl_runtime", None) is None:
        raise ProjectError(503, "ddl_unavailable", "Przetwarzanie DDL jest niedostępne.")
    with database.session() as session:
        row = session.execute(text("SELECT owner_subject FROM app.projects WHERE id=:id"), {"id": project_id}).first()
        try:
            if row is None:
                raise AccessDenied()
            request.app.state.access_policy.require_owner(actor, row[0])
        except AccessDenied:
            raise ProjectError(404, "PROJECT_NOT_FOUND", "Nie znaleziono projektu.") from None
    return actor, DdlRepository(database)


def public_attempt(row):
    keys = ("id", "project_id", "status", "schema_version_id", "launch_count", "next_attempt_at",
            "lease_expires_at", "diagnostics", "receipt_nonce")
    result = {("attempt_id" if key == "id" else key): row[key] for key in keys if key in row}
    return result


def publish_file(repo, artifacts, runtime, project_id, attempt_id, epoch, ref, content):
    with io_lock(runtime):
        repo.journal(project_id, attempt_id, epoch, UUID(ref.id))
        artifacts.put_at(ref, content)


@router.put("/ddl-attempts/{attempt_id}")
def reserve(project_id: UUID, attempt_id: UUID4, data: Reservation, request: Request):
    actor, repo = access(request, project_id)
    files = [file.model_dump() for file in data.files]
    validate_metadata(files, request.app.state.ddl_settings.limits())
    created = repo.reserve(project_id, actor.subject, attempt_id, data.page_id, files)
    state = repo.get(project_id, attempt_id, data.page_id)
    return JSONResponse(status_code=201 if created else 200, content=json.loads(json.dumps(public_attempt(state), default=str)))


@router.get("/ddl-attempts/{attempt_id}")
def attempt(project_id: UUID, attempt_id: UUID4, request: Request, x_ddl_page_id: UUID4 | None = Header(default=None)):
    _, repo = access(request, project_id)
    row = repo.get(project_id, attempt_id, x_ddl_page_id)
    if row is None:
        raise ProjectError(404, "DDL_ATTEMPT_NOT_FOUND", "Nie znaleziono próby.")
    return public_attempt(row)


@router.post("/ddl-attempts/{attempt_id}/lease")
def lease(project_id: UUID, attempt_id: UUID4, data: Page, request: Request):
    _, repo = access(request, project_id)
    return {"lease_expires_at": repo.renew(project_id, attempt_id, data.page_id)}


@router.post("/ddl-attempts/{attempt_id}/files", status_code=201)
async def upload(project_id: UUID, attempt_id: UUID4, request: Request, x_ddl_page_id: UUID4 = Header()):
    _, repo = await run_in_threadpool(access, request, project_id)
    files, epoch = await run_in_threadpool(repo.start_receiving, project_id, attempt_id, x_ddl_page_id)

    async def check_active():
        await run_in_threadpool(repo.renew, project_id, attempt_id, x_ddl_page_id, receiving=True)

    try:
        contents = await receive_multipart(request.headers.get("content-type", ""), request.stream(), files,
                                           request.app.state.ddl_settings.limits(), check_active)
        diagnostics = validate_content(contents)
        if diagnostics:
            await run_in_threadpool(repo.begin_cleanup, project_id, attempt_id, "REJECTED_INPUT", x_ddl_page_id, diagnostics)
            raise InputError("DDL_INPUT_INVALID", {"diagnostics": diagnostics})
        manifest = []
        for position, (name, content) in enumerate(contents):
            ref = ArtifactRef("project", str(uuid4()))
            await run_in_threadpool(publish_file, repo, request.app.state.artifacts, request.app.state.ddl_runtime,
                                    project_id, attempt_id, epoch, ref, content)
            manifest.append({"id": uuid4(), "position": position, "name": name, "size_bytes": len(content),
                             "sha256": sha256(content), "artifact_id": UUID(ref.id)})
        nonce = await run_in_threadpool(repo.staged, project_id, attempt_id, epoch, manifest)
        state = await run_in_threadpool(repo.get, project_id, attempt_id, x_ddl_page_id)
        return public_attempt(state) | {"receipt_nonce": nonce}
    except BaseException:
        await run_in_threadpool(repo.begin_cleanup, project_id, attempt_id, "CANCELLED", x_ddl_page_id)
        raise


@router.post("/ddl-attempts/{attempt_id}/receipt", status_code=202)
def receipt(project_id: UUID, attempt_id: UUID4, data: Receipt, request: Request):
    _, repo = access(request, project_id)
    return {"schema_version_id": repo.acknowledge(project_id, attempt_id, data.page_id, data.receipt_nonce)}


@router.post("/ddl-attempts/{attempt_id}/cancel")
def cancel(project_id: UUID, attempt_id: UUID4, request: Request, data: Page | None = None):
    _, repo = access(request, project_id)
    page = data.page_id if data else None
    row = repo.get(project_id, attempt_id, page)
    if row is None:
        raise ProjectError(404, "DDL_ATTEMPT_NOT_FOUND", "Nie znaleziono próby.")
    state = repo.begin_cleanup(project_id, attempt_id, "CANCELLED", page)
    return JSONResponse(status_code=200 if state == "CANCELLED" else 202, content={"status": state})


@router.get("/ddl-processing")
def processing(project_id: UUID, request: Request):
    actor, repo = access(request, project_id)
    row = repo.current()
    visible = row is not None and row["project_id"] == project_id and row["owner_subject"] == actor.subject
    return {"busy": row is not None, "attempt_id": row["id"] if visible else None,
            "status": row["status"] if visible else None}


def _version(repo, project_id, version_id):
    with repo.database.session() as session:
        row = session.execute(text("""SELECT v.*, a.diagnostics FROM app.schema_versions v
            JOIN app.ddl_attempts a ON a.id=v.attempt_id WHERE v.project_id=:project AND v.id=:id"""),
            {"project": project_id, "id": version_id}).mappings().first()
        if row is None:
            raise ProjectError(404, "SCHEMA_VERSION_NOT_FOUND", "Nie znaleziono wersji.")
        files = session.execute(text("""SELECT id, position, name, size_bytes, sha256 FROM app.ddl_attempt_files
            WHERE attempt_id=:attempt ORDER BY position"""), {"attempt": row["attempt_id"]}).mappings().all()
        return dict(row) | {"files": [dict(file) for file in files]}


@router.get("/schema-versions")
def versions(project_id: UUID, request: Request):
    _, repo = access(request, project_id)
    with repo.database.session() as session:
        ids = list(session.execute(text("SELECT id FROM app.schema_versions WHERE project_id=:project ORDER BY revision_no DESC"),
                                   {"project": project_id}).scalars())
    return {"items": [_version(repo, project_id, version_id) for version_id in ids]}


@router.get("/schema-versions/{version_id}")
def version(project_id: UUID, version_id: UUID4, request: Request):
    _, repo = access(request, project_id)
    return _version(repo, project_id, version_id)


@router.get("/schema-versions/{version_id}/files/{file_id}")
def file_contents(project_id: UUID, version_id: UUID4, file_id: UUID4, request: Request):
    from urllib.parse import quote

    _, repo = access(request, project_id)
    with repo.database.session() as session:
        row = session.execute(text("""SELECT f.name, f.artifact_id FROM app.ddl_attempt_files f
            JOIN app.schema_versions v ON v.attempt_id=f.attempt_id
            WHERE v.project_id=:project AND v.id=:version AND f.id=:file"""),
            {"project": project_id, "version": version_id, "file": file_id}).mappings().first()
    if row is None:
        raise ProjectError(404, "DDL_FILE_NOT_FOUND", "Nie znaleziono pliku.")
    content = request.app.state.artifacts.get(ArtifactRef("project", str(row["artifact_id"])))
    return Response(content, media_type="application/sql", headers={
        "Content-Disposition": f"attachment; filename=ddl.sql; filename*=UTF-8''{quote(row['name'], safe='')}"})


@router.get("/schema-versions/{version_id}/analysis")
def analysis(project_id: UUID, version_id: UUID4, request: Request):
    _, repo = access(request, project_id)
    _version(repo, project_id, version_id)
    with repo.database.session() as session:
        row = session.execute(text("""SELECT analysis FROM app.schema_interpretations
            WHERE project_id=:project AND schema_version_id=:version ORDER BY revision_no DESC LIMIT 1"""),
            {"project": project_id, "version": version_id}).first()
    if row is None:
        raise InputError("DDL_ANALYSIS_NOT_AVAILABLE")
    return row[0]
