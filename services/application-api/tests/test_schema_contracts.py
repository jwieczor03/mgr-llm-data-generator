from uuid import uuid4

import pytest
from application_api.schema_contracts import (
    AnalysisProfile,
    DdlBundle,
    Diagnostic,
    ParsedSchema,
    SchemaAnalysis,
    StagedDdlAnalyzer,
)
from pydantic import ValidationError


def test_checkpoint_resume_and_mismatch():
    bundle = DdlBundle(schema_version_id=uuid4(), manifest_hash="a" * 64, files=[])
    profile = AnalysisProfile(adapter_version="1", library_version="1", postgres_version="18", profile="mvp")
    parsed = ParsedSchema(schema_version_id=bundle.schema_version_id, tables=[], columns=[], constraints=[],
                          relations=[], diagnostics=[])
    calls, checkpoints = [], []

    class Parser:
        def parse(self, bundle, profile):
            calls.append("parse")
            return parsed

    class Support:
        def diagnose(self, parsed, profile):
            calls.append("support")
            return SchemaAnalysis(**parsed.model_dump(), contract_version=1, analysis_profile=profile, supported=True)

    analyzer = StagedDdlAnalyzer(Parser(), Support(), checkpoints.append)
    analyzer.analyze(bundle, profile)
    assert calls == ["parse", "support"]
    assert checkpoints[0].valid_for(bundle, profile)
    calls.clear()
    StagedDdlAnalyzer(Parser(), Support(), checkpoints.append, checkpoints[0]).analyze(bundle, profile)
    assert calls == ["support"]
    calls.clear()
    tampered = checkpoints[0].model_copy(update={"model_hash": "0" * 64})
    StagedDdlAnalyzer(Parser(), Support(), checkpoints.append, tampered).analyze(bundle, profile)
    assert calls == ["parse", "support"]


def test_supported_consistent_with_diagnostics():
    args = dict(contract_version=1, schema_version_id=uuid4(), tables=[], columns=[], constraints=[], relations=[],
                analysis_profile=AnalysisProfile(adapter_version="1", library_version="1", postgres_version="18", profile="mvp"))
    error = Diagnostic(code="DDL_SYNTAX_ERROR", message="Błąd", severity="error", scope="bundle", object_ids=[])
    with pytest.raises(ValidationError):
        SchemaAnalysis(**args, supported=True, diagnostics=[error])
    with pytest.raises(ValidationError):
        SchemaAnalysis(**args, supported=False, diagnostics=[])
    assert not SchemaAnalysis(**args, supported=False, diagnostics=[error]).supported
