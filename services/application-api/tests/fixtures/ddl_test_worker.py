"""Test-only adapter executed by the actual worker entry point."""
import hashlib
import sys
import time

from application_api.ddl_worker import main
from application_api.schema_contracts import canonical_json

mode = sys.argv.pop(1)


def adapter(request, emit):
    bundle, profile = request["bundle"], request["profile"]
    if mode == "resume" and request.get("checkpoint") is None:
        return {"type": "error", "code": "MISSING_CHECKPOINT"}
    parsed = {"schema_version_id": bundle["schema_version_id"], "tables": [], "columns": [],
              "constraints": [], "relations": [], "diagnostics": []}
    checkpoint = {"contract_version": 2, "schema_version_id": bundle["schema_version_id"],
                  "manifest_hash": bundle["manifest_hash"], "analysis_profile": profile, "parsed": parsed,
                  "model_hash": hashlib.sha256(canonical_json(parsed)).hexdigest()}
    emit({"type": "checkpoint", "checkpoint": checkpoint})
    if mode == "wait":
        time.sleep(60)
    if mode == "fail":
        return {"type": "error", "code": "DDL_WORKER_FAILED"}
    if mode == "reject":
        parsed["diagnostics"] = [{"code": "DDL_SYNTAX_ERROR", "message": "Błąd", "severity": "error",
                                  "scope": "bundle", "object_ids": [], "location": None}]
    result = {**parsed, "contract_version": 1, "analysis_profile": profile, "supported": mode != "reject"}
    return {"type": "result", "contract_version": 1, "schema_version_id": bundle["schema_version_id"],
            "manifest_hash": bundle["manifest_hash"], "analysis_profile": profile, "analysis": result}


raise SystemExit(main(adapter))
