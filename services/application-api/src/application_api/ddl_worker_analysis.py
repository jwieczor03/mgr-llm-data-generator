"""Run T3 and persist its checkpoint; T4 remains unavailable."""
import base64
import hashlib

from application_api.ddl_parser import DdlParser
from application_api.schema_contracts import (
    AnalysisProfile,
    Checkpoint,
    DdlBundle,
    canonical_json,
    manifest_digest,
)


def analyze(request, emit):
    bundle = DdlBundle.model_validate(request['bundle'])
    if manifest_digest(bundle.files) != bundle.manifest_hash:
        raise ValueError('manifest hash mismatch')
    profile = AnalysisProfile.model_validate(request['profile'])
    if (profile.adapter_version, profile.library_version, profile.postgres_version, profile.profile) != (
        'pglast-1', '8.9', '18', 'postgres-mvp-v1'
    ):
        return {'type': 'error', 'code': 'DDL_ANALYZER_UNAVAILABLE'}
    raw_checkpoint = request.get('checkpoint')
    checkpoint = Checkpoint.model_validate(raw_checkpoint) if raw_checkpoint else None
    if checkpoint is None or not checkpoint.valid_for(bundle, profile):
        data = request['files_base64']
        if len(data) != len(bundle.files):
            raise ValueError('file count differs from manifest')
        contents = {file.file_id: base64.b64decode(item, validate=True) for file, item in zip(bundle.files, data)}
        parsed = DdlParser(lambda file: contents[file.file_id]).parse(bundle, profile)
        model_hash = hashlib.sha256(canonical_json(parsed.model_dump(mode='json'))).hexdigest()
        checkpoint = Checkpoint(contract_version=1, schema_version_id=bundle.schema_version_id,
                                manifest_hash=bundle.manifest_hash, analysis_profile=profile,
                                parsed=parsed, model_hash=model_hash)
        emit({'type': 'checkpoint', 'checkpoint': checkpoint.model_dump(mode='json')})
    return {'type': 'error', 'code': 'DDL_ANALYZER_UNAVAILABLE'}
