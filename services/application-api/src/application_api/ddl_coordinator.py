"""Recoverable singleton DDL coordinator backed by PostgreSQL and a POSIX worker."""
import base64
import threading
from pathlib import Path

from sqlalchemy import text

from application_api.artifact_store import ArtifactRef
from application_api.ddl_leader import LeaderDatabase
from application_api.ddl_process import WorkerProcess
from application_api.ddl_repository import (
    ACTIVE_ANALYSIS,
    PRE_ACK,
    DdlRepository,
    now,
    sha256,
)
from application_api.ddl_runtime import io_lock, worker_stopped
from application_api.schema_contracts import AnalysisProfile, Checkpoint

COORDINATOR_LOCK_KEY = 1395733557


class DdlCoordinator:
    def __init__(self, database, artifacts, runtime: Path, worker_timeout=120, worker_factory=WorkerProcess):
        self.database, self.artifacts, self.runtime = database, artifacts, runtime
        self.worker_timeout = worker_timeout
        self.worker_factory = worker_factory
        self.stop_event = threading.Event()
        self.ready_event = threading.Event()
        self.thread = None
        self.job = None
        self.worker = None
        self.worker_attempt = None

    def start(self):
        self.thread = threading.Thread(target=self._loop, name="ddl-coordinator", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.worker:
            self.worker.terminate()
        if self.thread:
            self.thread.join(timeout=10)

    def _loop(self):
        while not self.stop_event.is_set():
            leader = None
            try:
                with self.database.engine.connect() as connection:
                    # Closing a pooled connection would otherwise retain its session lock.
                    connection.detach()
                    locked = connection.execute(text("SELECT pg_try_advisory_lock(:key)"),
                                                {"key": COORDINATOR_LOCK_KEY}).scalar_one()
                    connection.commit()
                    if not locked:
                        self.stop_event.wait(1)
                        continue
                    leader = LeaderDatabase(connection, COORDINATOR_LOCK_KEY)
                    repo = DdlRepository(leader)
                    try:
                        recovery = True
                        while not self.stop_event.is_set():
                            leader.heartbeat()
                            row = repo.current()
                            if row:
                                self._step(repo, row, recovery)
                            self.ready_event.set()
                            # A prior generation's job may still be exiting after lock loss.
                            # Keep recovery enabled until that job has actually stopped.
                            if not (recovery and row and row["status"] == "ANALYZING"
                                    and self.job and self.job.is_alive()):
                                recovery = False
                            self.stop_event.wait(.25)
                    finally:
                        # Retire under the same mutex before closing the physical session.
                        leader.retire()
            except Exception:
                if leader:
                    leader.retire()
                if self.worker:
                    self.worker.terminate()
                self.stop_event.wait(1)
            finally:
                if leader:
                    leader.retire()
        if self.job:
            self.job.join(timeout=10)

    def _step(self, repo, row, recovery):
        attempt, status = row["id"], row["status"]
        if status in PRE_ACK and (recovery or row["lease_expires_at"] <= now()):
            repo.begin_cleanup(row["project_id"], attempt, "EXPIRED", pre_ack_only=True,
                               expired_only=not recovery)
            return
        if status in ("CANCELLING", "CLEANUP_FAILED"):
            if self.worker_attempt == attempt and self.worker:
                self.worker.terminate()
            if self.job and self.job.is_alive():
                return
            if status == "CLEANUP_FAILED" and row["next_attempt_at"] and row["next_attempt_at"] > now() and not recovery:
                return
            self._cleanup(repo, attempt)
            return
        if status in ACTIVE_ANALYSIS and not (self.job and self.job.is_alive()):
            launch = repo.launch(attempt, recovery=recovery)
            if launch:
                self.worker = self.worker_factory(self.runtime, self.worker_timeout)
                self.worker_attempt = attempt
                self.job = threading.Thread(target=self._run, args=(repo, self.worker, attempt, launch), daemon=True)
                self.job.start()

    def _run(self, repo, worker, attempt, launch):
        try:
            version = launch["version"]
            bundle = repo.bundle(attempt, version)
            profile = AnalysisProfile.model_validate_json(version["analysis_profile"])
            checkpoint = None
            if launch["checkpoint"]:
                try:
                    candidate = Checkpoint.model_validate(launch["checkpoint"])
                    if candidate.valid_for(bundle, profile):
                        checkpoint = candidate.model_dump(mode="json")
                except ValueError:
                    pass
            data = []
            for file in bundle.files:
                content = self.artifacts.get(ArtifactRef("project", str(file.artifact_id)))
                if len(content) != file.size_bytes or sha256(content) != file.sha256:
                    raise ValueError("artifact mismatch")
                data.append(base64.b64encode(content).decode("ascii"))
            terminal = []

            def message_received(message):
                kind = message.get("type")
                if kind == "checkpoint" and not terminal:
                    repo.save_checkpoint(attempt, launch["epoch"], bundle, profile, message.get("checkpoint"))
                elif kind in ("result", "error") and not terminal:
                    terminal.append(message)
                else:
                    raise ValueError("invalid worker protocol")

            payload = {"bundle": bundle.model_dump(mode="json"), "profile": profile.model_dump(mode="json"),
                       "files_base64": data, "checkpoint": checkpoint}
            outcome = worker.run(payload, on_message=message_received)
            code = outcome.error
            if code is None:
                if len(terminal) != 1:
                    raise ValueError("missing terminal message")
                final = terminal[0]
                if final["type"] == "result":
                    if (final.get("contract_version") != 1 or final.get("schema_version_id") != str(bundle.schema_version_id)
                            or final.get("manifest_hash") != bundle.manifest_hash
                            or final.get("analysis_profile") != profile.model_dump(mode="json")):
                        raise ValueError("result envelope mismatch")
                    repo.publish(attempt, launch["epoch"], bundle, profile, final.get("analysis"))
                    return
                code = final.get("code")
            repo.worker_failed(attempt, launch["epoch"], code or "DDL_WORKER_PROTOCOL_ERROR")
        except Exception:
            try:
                repo.worker_failed(attempt, launch["epoch"], "DDL_WORKER_PROTOCOL_ERROR")
            except Exception:
                pass  # A failed database connection is recovered by the next elected coordinator.
        finally:
            self.worker_attempt = None

    def _cleanup(self, repo, attempt):
        try:
            with worker_stopped(self.runtime), io_lock(self.runtime):
                for artifact in repo.cleanup_files(attempt):
                    self.artifacts.delete(ArtifactRef("project", str(artifact)))
                repo.finish_cleanup(attempt)
        except BlockingIOError:
            return
        except Exception:
            repo.cleanup_failed(attempt)
