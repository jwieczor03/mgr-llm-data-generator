"""Analyze a bundle in stages and emit a resumable parser checkpoint."""
import base64

from application_api.ddl_parser import DdlParser
from application_api.ddl_support import DdlSupport
from application_api.schema_contracts import (
    AnalysisProfile,
    Checkpoint,
    DdlBundle,
    StagedDdlAnalyzer,
    manifest_digest,
)


def analyze(request, emit):
    bundle = DdlBundle.model_validate(request['bundle'])
    if manifest_digest(bundle.files) != bundle.manifest_hash:
        raise ValueError('manifest hash mismatch')
    profile = AnalysisProfile.model_validate(request['profile'])
    if (profile.adapter_version not in {'pglast-2', 'pglast-3'} or
            (profile.library_version, profile.postgres_version, profile.profile) != ('8.9', '18', 'postgres-mvp-v1')):
        return {'type': 'error', 'code': 'DDL_ANALYZER_UNAVAILABLE'}
    raw_checkpoint = request.get('checkpoint')
    checkpoint = Checkpoint.model_validate(raw_checkpoint) if raw_checkpoint else None
    data = request['files_base64']
    if len(data) != len(bundle.files):
        raise ValueError('file count differs from manifest')
    contents = {file.file_id: base64.b64decode(item, validate=True) for file, item in zip(bundle.files, data)}
    analyzer = StagedDdlAnalyzer(DdlParser(lambda file: contents[file.file_id]), DdlSupport(),
                                 lambda ck: emit({'type': 'checkpoint', 'checkpoint': ck.model_dump(mode='json')}),
                                 checkpoint)
    analysis = analyzer.analyze(bundle, profile)
    return {'type': 'result', 'contract_version': 1, 'schema_version_id': str(bundle.schema_version_id),
            'manifest_hash': bundle.manifest_hash, 'analysis_profile': profile.model_dump(mode='json'),
            'analysis': analysis.model_dump(mode='json')}
