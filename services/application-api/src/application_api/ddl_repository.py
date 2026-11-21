"""Transactional operations for DDL attempts; no filesystem I/O under row locks."""
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import text

from application_api.ddl_input import InputError
from application_api.schema_contracts import (
    AnalysisProfile,
    Checkpoint,
    DdlBundle,
    ManifestFile,
    SchemaAnalysis,
    canonical_json,
)

LEASE_SECONDS = 120
PRE_ACK = ("RESERVED", "RECEIVING", "STAGED")
ACTIVE_ANALYSIS = ("ANALYSIS_PENDING", "ANALYZING", "RETRY_WAIT")
TERMINAL = ("SUCCEEDED", "REJECTED_INPUT", "REJECTED_DDL", "FAILED_TECHNICAL", "CANCELLED", "EXPIRED")
PROFILE = AnalysisProfile(adapter_version="unavailable-1", library_version="30.33.0", postgres_version="18",
                          profile="postgres-mvp-v1")


def now():
    return datetime.now(timezone.utc)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _row(session, statement, params):
    return session.execute(text(statement), params).mappings().first()


def _slot(session):
    return _row(session, "SELECT attempt_id FROM app.ddl_slot WHERE singleton=1 FOR UPDATE", {})["attempt_id"]


def _attempt(session, project_id, attempt_id):
    return _row(session, "SELECT * FROM app.ddl_attempts WHERE project_id=:project AND id=:attempt FOR UPDATE",
                {"project": project_id, "attempt": attempt_id})


def _page(row, page_id):
    if row is None:
        raise InputError("DDL_ATTEMPT_NOT_FOUND")
    if row["page_id"] != page_id:
        raise InputError("DDL_ATTEMPT_CLOSED")


class DdlRepository:
    def __init__(self, database):
        self.database = database

    def reserve(self, project_id, owner, attempt_id, page_id, files):
        digest = sha256(canonical_json(files))
        with self.database.session() as session:
            slot = _slot(session)
            row = _attempt(session, project_id, attempt_id)
            if row is not None:
                if row["owner_subject"] != owner or row["page_id"] != page_id or row["reservation_hash"] != digest:
                    raise InputError("DDL_ATTEMPT_CONFLICT")
                return False
            existing = _row(session, "SELECT id FROM app.ddl_attempts WHERE id=:id", {"id": attempt_id})
            if existing is not None:
                raise InputError("DDL_ATTEMPT_NOT_FOUND")
            if slot is not None:
                raise InputError("DDL_PROCESSING_IN_PROGRESS")
            session.execute(text("""INSERT INTO app.ddl_attempts
                (id, project_id, owner_subject, page_id, reservation, reservation_hash, status, lease_expires_at)
                VALUES (:id, :project, :owner, :page, CAST(:reservation AS jsonb), :hash, 'RESERVED', :lease)"""),
                {"id": attempt_id, "project": project_id, "owner": owner, "page": page_id,
                 "reservation": json.dumps(files, ensure_ascii=False), "hash": digest,
                 "lease": now() + timedelta(seconds=LEASE_SECONDS)})
            session.execute(text("UPDATE app.ddl_slot SET attempt_id=:id WHERE singleton=1"), {"id": attempt_id})
            return True

    def get(self, project_id, attempt_id, page_id=None):
        with self.database.session() as session:
            row = _attempt(session, project_id, attempt_id)
            if row is None:
                return None
            result = dict(row)
            if row["status"] in PRE_ACK:
                _page(row, page_id)
            if (row["status"] != "STAGED" or row["page_id"] != page_id
                    or row["lease_expires_at"] <= now()):
                result.pop("receipt_nonce", None)
            version = _row(session, "SELECT id FROM app.schema_versions WHERE attempt_id=:id", {"id": attempt_id})
            result["schema_version_id"] = version["id"] if version else None
            return result

    def renew(self, project_id, attempt_id, page_id, *, receiving=False):
        with self.database.session() as session:
            slot = _slot(session)
            row = _attempt(session, project_id, attempt_id)
            _page(row, page_id)
            if slot != attempt_id or row["status"] not in PRE_ACK or row["lease_expires_at"] <= now():
                raise InputError("DDL_ATTEMPT_CLOSED")
            if receiving and row["status"] != "RECEIVING":
                raise InputError("DDL_ATTEMPT_CLOSED")
            expires = now() + timedelta(seconds=LEASE_SECONDS)
            session.execute(text("UPDATE app.ddl_attempts SET lease_expires_at=:lease WHERE id=:id"),
                            {"lease": expires, "id": attempt_id})
            return expires

    def start_receiving(self, project_id, attempt_id, page_id):
        with self.database.session() as session:
            slot = _slot(session)
            row = _attempt(session, project_id, attempt_id)
            _page(row, page_id)
            if row["status"] in ("RECEIVING", "STAGED", *ACTIVE_ANALYSIS, "SUCCEEDED", "REJECTED_DDL", "FAILED_TECHNICAL"):
                raise InputError("DDL_UPLOAD_ALREADY_RECEIVED")
            if slot != attempt_id or row["lease_expires_at"] is None or row["lease_expires_at"] <= now():
                raise InputError("DDL_ATTEMPT_CLOSED")
            if row["status"] != "RESERVED":
                raise InputError("DDL_ATTEMPT_CLOSED")
            session.execute(text("UPDATE app.ddl_attempts SET status='RECEIVING' WHERE id=:id"), {"id": attempt_id})
            return row["reservation"], row["execution_epoch"]

    def journal(self, project_id, attempt_id, epoch, artifact_id):
        with self.database.session() as session:
            slot = _slot(session)
            row = _attempt(session, project_id, attempt_id)
            if (slot != attempt_id or row is None or row["status"] != "RECEIVING"
                    or row["execution_epoch"] != epoch or row["lease_expires_at"] <= now()):
                raise InputError("DDL_ATTEMPT_CLOSED")
            session.execute(text("INSERT INTO app.ddl_artifact_journal (id, attempt_id, artifact_id) VALUES (:id,:attempt,:artifact)"),
                            {"id": uuid4(), "attempt": attempt_id, "artifact": artifact_id})

    def staged(self, project_id, attempt_id, epoch, manifest):
        with self.database.session() as session:
            slot = _slot(session)
            row = _attempt(session, project_id, attempt_id)
            if (slot != attempt_id or row is None or row["status"] != "RECEIVING"
                    or row["execution_epoch"] != epoch or row["lease_expires_at"] <= now()):
                raise InputError("DDL_ATTEMPT_CLOSED")
            for file in manifest:
                session.execute(text("""INSERT INTO app.ddl_attempt_files
                    (id, attempt_id, position, name, name_key, size_bytes, sha256, artifact_id)
                    VALUES (:id,:attempt,:position,:name,:name_key,:size_bytes,:sha256,:artifact_id)"""),
                    file | {"attempt": attempt_id, "name_key": file["name"].casefold()})
            nonce = secrets.token_urlsafe(32)
            session.execute(text("""UPDATE app.ddl_attempts SET status='STAGED', receipt_nonce=:nonce,
                lease_expires_at=:lease WHERE id=:id"""),
                {"id": attempt_id, "nonce": nonce, "lease": now() + timedelta(seconds=LEASE_SECONDS)})
            return nonce

    def acknowledge(self, project_id, attempt_id, page_id, nonce):
        with self.database.session() as session:
            slot = _slot(session)
            row = _attempt(session, project_id, attempt_id)
            _page(row, page_id)
            version = _row(session, "SELECT id FROM app.schema_versions WHERE attempt_id=:id", {"id": attempt_id})
            try:
                nonce_hash = sha256(nonce.encode("ascii"))
            except UnicodeEncodeError:
                raise InputError("DDL_RECEIPT_CONFLICT") from None
            if version and row["status"] not in ("CANCELLING", "CLEANUP_FAILED", "CANCELLED", "EXPIRED"):
                if row["receipt_nonce_hash"] and secrets.compare_digest(row["receipt_nonce_hash"], nonce_hash):
                    return version["id"]
                raise InputError("DDL_RECEIPT_CONFLICT")
            if (slot != attempt_id or row["status"] != "STAGED" or row["lease_expires_at"] <= now()):
                raise InputError("DDL_ATTEMPT_CLOSED")
            if not row["receipt_nonce"] or not secrets.compare_digest(row["receipt_nonce"], nonce):
                raise InputError("DDL_RECEIPT_CONFLICT")
            files = session.execute(text("""SELECT id, position, name, size_bytes, sha256, artifact_id
                FROM app.ddl_attempt_files WHERE attempt_id=:id ORDER BY position"""), {"id": attempt_id}).mappings().all()
            manifest = [{key: str(value) if key in ("id", "artifact_id") else value for key, value in file.items()}
                        for file in files]
            manifest_hash = sha256(canonical_json(manifest))
            revision = session.execute(text("SELECT COALESCE(MAX(revision_no),0)+1 FROM app.schema_versions WHERE project_id=:id"),
                                       {"id": project_id}).scalar_one()
            version_id = uuid4()
            session.execute(text("""INSERT INTO app.schema_versions
                (id, project_id, attempt_id, revision_no, manifest_hash, analysis_profile, status)
                VALUES (:id,:project,:attempt,:revision,:hash,:profile,'ANALYSIS_PENDING')"""),
                {"id": version_id, "project": project_id, "attempt": attempt_id,
                 "revision": revision, "hash": manifest_hash,
                 "profile": PROFILE.model_dump_json()})
            session.execute(text("""UPDATE app.ddl_attempts SET status='ANALYSIS_PENDING', receipt_nonce=NULL,
                receipt_nonce_hash=:hash, lease_expires_at=NULL WHERE id=:id"""), {"id": attempt_id, "hash": nonce_hash})
            return version_id

    def begin_cleanup(self, project_id, attempt_id, target, page_id=None, diagnostics=None, *, upload_epoch=None):
        with self.database.session() as session:
            slot = _slot(session)
            row = _attempt(session, project_id, attempt_id)
            if row is None:
                return None
            # A failed upload may clean up only the same still-unacknowledged transfer.
            if upload_epoch is not None and (row["status"] not in PRE_ACK or row["execution_epoch"] != upload_epoch):
                return None
            if row["status"] in PRE_ACK and page_id is not None:
                _page(row, page_id)
            if row["status"] in TERMINAL:
                return row["status"]
            if slot != attempt_id:
                raise InputError("DDL_ATTEMPT_CLOSED")
            if row["status"] not in ("CANCELLING", "CLEANUP_FAILED"):
                session.execute(text("""UPDATE app.ddl_attempts SET status='CANCELLING',
                    execution_epoch=execution_epoch+1, receipt_nonce=NULL, cleanup_target=:target,
                    diagnostics=CAST(:diagnostics AS jsonb), next_attempt_at=NULL WHERE id=:id"""),
                    {"id": attempt_id, "target": target, "diagnostics": json.dumps(diagnostics)})
            return "CANCELLING"

    def cleanup_files(self, attempt_id):
        with self.database.session() as session:
            return list(session.execute(text("SELECT artifact_id FROM app.ddl_artifact_journal WHERE attempt_id=:id"),
                                        {"id": attempt_id}).scalars())

    def cleanup_failed(self, attempt_id):
        with self.database.session() as session:
            if _slot(session) != attempt_id:
                return
            session.execute(text("""UPDATE app.ddl_attempts SET status='CLEANUP_FAILED', next_attempt_at=:next
                WHERE id=:id AND status IN ('CANCELLING','CLEANUP_FAILED')"""),
                {"id": attempt_id, "next": now() + timedelta(seconds=30)})

    def finish_cleanup(self, attempt_id):
        with self.database.session() as session:
            if _slot(session) != attempt_id:
                return
            row = _row(session, "SELECT * FROM app.ddl_attempts WHERE id=:id FOR UPDATE", {"id": attempt_id})
            if row is None or row["status"] not in ("CANCELLING", "CLEANUP_FAILED"):
                return
            session.execute(text("DELETE FROM app.schema_versions WHERE attempt_id=:id"), {"id": attempt_id})
            session.execute(text("DELETE FROM app.ddl_attempt_files WHERE attempt_id=:id"), {"id": attempt_id})
            session.execute(text("DELETE FROM app.ddl_artifact_journal WHERE attempt_id=:id"), {"id": attempt_id})
            session.execute(text("""UPDATE app.ddl_attempts SET status=cleanup_target, cleanup_target=NULL,
                checkpoint=NULL, next_attempt_at=NULL WHERE id=:id"""), {"id": attempt_id})
            session.execute(text("UPDATE app.ddl_slot SET attempt_id=NULL WHERE singleton=1"))

    def current(self):
        with self.database.session() as session:
            return _row(session, """SELECT a.* FROM app.ddl_slot s JOIN app.ddl_attempts a ON a.id=s.attempt_id
                WHERE s.singleton=1""", {})

    def launch(self, attempt_id, *, recovery=False):
        with self.database.session() as session:
            if _slot(session) != attempt_id:
                return None
            row = _row(session, "SELECT * FROM app.ddl_attempts WHERE id=:id FOR UPDATE", {"id": attempt_id})
            if row is None or row["status"] not in ACTIVE_ANALYSIS:
                return None
            if row["status"] == "RETRY_WAIT" and row["next_attempt_at"] > now():
                return None
            if row["status"] == "ANALYZING":
                if recovery:
                    # Fence the lost execution before persisting its retry deadline.
                    session.execute(text("UPDATE app.ddl_attempts SET execution_epoch=execution_epoch+1 WHERE id=:id"),
                                    {"id": attempt_id})
                    self._worker_failed_locked(session, row, "DDL_WORKER_FAILED")
                return None
            if row["launch_count"] >= 4:
                self._fail_locked(session, attempt_id, "DDL_WORKER_FAILED")
                return None
            session.execute(text("""UPDATE app.ddl_attempts SET status='ANALYZING', execution_epoch=execution_epoch+1,
                launch_count=launch_count+1, next_attempt_at=NULL WHERE id=:id"""), {"id": attempt_id})
            version = _row(session, "SELECT * FROM app.schema_versions WHERE attempt_id=:id", {"id": attempt_id})
            return {"epoch": row["execution_epoch"] + 1, "launch_count": row["launch_count"] + 1,
                    "version": dict(version), "checkpoint": row["checkpoint"]}

    def worker_failed(self, attempt_id, epoch, code):
        with self.database.session() as session:
            if _slot(session) != attempt_id:
                return
            row = _row(session, "SELECT * FROM app.ddl_attempts WHERE id=:id FOR UPDATE", {"id": attempt_id})
            if row is None or row["status"] != "ANALYZING" or row["execution_epoch"] != epoch:
                return
            self._worker_failed_locked(session, row, code)

    @staticmethod
    def _worker_failed_locked(session, row, code):
        attempt_id = row["id"]
        if row["launch_count"] >= 4:
            DdlRepository._fail_locked(session, attempt_id, code)
        else:
            delay = (1, 5, 15)[row["launch_count"] - 1]
            session.execute(text("""UPDATE app.ddl_attempts SET status='RETRY_WAIT', next_attempt_at=:next,
                diagnostics=CAST(:diagnostics AS jsonb) WHERE id=:id"""),
                {"id": attempt_id, "next": now() + timedelta(seconds=delay),
                 "diagnostics": json.dumps([{"code": code}])})

    @staticmethod
    def _fail_locked(session, attempt_id, code):
        session.execute(text("""UPDATE app.ddl_attempts SET status='FAILED_TECHNICAL', next_attempt_at=NULL,
            diagnostics=CAST(:diagnostics AS jsonb) WHERE id=:id"""),
            {"id": attempt_id, "diagnostics": json.dumps([{"code": code}])})
        session.execute(text("UPDATE app.schema_versions SET status='FAILED_TECHNICAL' WHERE attempt_id=:id"), {"id": attempt_id})
        session.execute(text("UPDATE app.ddl_slot SET attempt_id=NULL WHERE singleton=1"))

    def bundle(self, attempt_id, version):
        with self.database.session() as session:
            rows = session.execute(text("""SELECT id, position, name, size_bytes, sha256, artifact_id
                FROM app.ddl_attempt_files WHERE attempt_id=:id ORDER BY position"""), {"id": attempt_id}).mappings().all()
            files = [ManifestFile(file_id=row["id"], position=row["position"], name=row["name"],
                                  size_bytes=row["size_bytes"], sha256=row["sha256"], artifact_id=row["artifact_id"])
                     for row in rows]
            return DdlBundle(schema_version_id=version["id"], manifest_hash=version["manifest_hash"], files=files)

    def save_checkpoint(self, attempt_id, epoch, bundle, profile, checkpoint):
        checkpoint = Checkpoint.model_validate(checkpoint)
        if not checkpoint.valid_for(bundle, profile):
            raise ValueError("checkpoint mismatch")
        with self.database.session() as session:
            if _slot(session) != attempt_id:
                raise ValueError("slot lost")
            row = _row(session, "SELECT * FROM app.ddl_attempts WHERE id=:id FOR UPDATE", {"id": attempt_id})
            if row is None or row["status"] != "ANALYZING" or row["execution_epoch"] != epoch:
                raise ValueError("stale worker")
            version = _row(session, "SELECT * FROM app.schema_versions WHERE attempt_id=:id", {"id": attempt_id})
            if (version is None or version["id"] != bundle.schema_version_id
                    or version["manifest_hash"] != bundle.manifest_hash
                    or AnalysisProfile.model_validate_json(version["analysis_profile"]) != profile):
                raise ValueError("version mismatch")
            session.execute(text("UPDATE app.ddl_attempts SET checkpoint=CAST(:checkpoint AS jsonb) WHERE id=:id"),
                            {"id": attempt_id, "checkpoint": checkpoint.model_dump_json()})

    def publish(self, attempt_id, epoch, bundle, profile, document):
        analysis = SchemaAnalysis.model_validate(document)
        if analysis.schema_version_id != bundle.schema_version_id or analysis.analysis_profile != profile:
            raise ValueError("analysis mismatch")
        with self.database.session() as session:
            if _slot(session) != attempt_id:
                raise ValueError("slot lost")
            row = _row(session, "SELECT * FROM app.ddl_attempts WHERE id=:id FOR UPDATE", {"id": attempt_id})
            if row is None or row["status"] != "ANALYZING" or row["execution_epoch"] != epoch:
                raise ValueError("stale worker")
            version = _row(session, "SELECT * FROM app.schema_versions WHERE attempt_id=:id", {"id": attempt_id})
            if (version is None or version["id"] != bundle.schema_version_id
                    or version["manifest_hash"] != bundle.manifest_hash
                    or AnalysisProfile.model_validate_json(version["analysis_profile"]) != profile):
                raise ValueError("version mismatch")
            status = "SUCCEEDED" if analysis.supported else "REJECTED_DDL"
            session.execute(text("""INSERT INTO app.schema_interpretations
                (id, project_id, schema_version_id, revision_no, analysis_profile, analysis)
                VALUES (:id,:project,:version,1,:profile,CAST(:analysis AS jsonb))"""),
                {"id": uuid4(), "project": row["project_id"], "version": version["id"],
                 "profile": profile.model_dump_json(), "analysis": analysis.model_dump_json()})
            session.execute(text("UPDATE app.schema_versions SET status=:status WHERE id=:id"),
                            {"status": status, "id": version["id"]})
            session.execute(text("""UPDATE app.ddl_attempts SET status=:status, diagnostics=CAST(:diagnostics AS jsonb),
                checkpoint=NULL WHERE id=:id"""),
                {"id": attempt_id, "status": status,
                 "diagnostics": json.dumps([d.model_dump(mode="json") for d in analysis.diagnostics])})
            if analysis.supported:
                session.execute(text("""UPDATE app.projects SET default_schema_version_id=:version,
                    requirements_review_required=true WHERE id=:project"""),
                    {"version": version["id"], "project": row["project_id"]})
            session.execute(text("UPDATE app.ddl_slot SET attempt_id=NULL WHERE singleton=1"))
