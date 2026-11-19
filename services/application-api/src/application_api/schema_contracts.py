"""Application-owned DDL analysis contracts, independent of the parser library."""
import hashlib
import json
from collections.abc import Callable
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AnalysisProfile(Contract):
    adapter_version: str
    library_version: str
    postgres_version: str
    profile: str


class SourceLocation(Contract):
    file_id: UUID
    line: int = Field(ge=1)
    column: int = Field(ge=1)


class Diagnostic(Contract):
    code: str
    message: str
    severity: Literal["error", "warning"]
    scope: Literal["bundle", "file", "object"]
    object_ids: list[UUID]
    location: SourceLocation | None = None


class ManifestFile(Contract):
    file_id: UUID
    name: str
    position: int = Field(ge=0)
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact_id: UUID


class DdlBundle(Contract):
    schema_version_id: UUID
    manifest_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    files: list[ManifestFile]


class SqlType(Contract):
    name: str
    length: int | None = Field(default=None, ge=0)
    precision: int | None = Field(default=None, ge=0)
    scale: int | None = None


class Expression(Contract):
    op: str
    args: list["Expression"] = Field(default_factory=list)
    literal_type: str | None = None
    literal_value: str | None = None
    original: str | None = None


class Table(Contract):
    table_id: UUID
    schema_name: str
    name: str
    original_name: str
    location: SourceLocation | None = None


class Column(Contract):
    column_id: UUID
    table_id: UUID
    position: int = Field(ge=0)
    name: str
    original_name: str
    type: SqlType
    nullable: bool
    default: Expression | None = None
    automatic_id: str | None = None
    location: SourceLocation | None = None


class Constraint(Contract):
    constraint_id: UUID
    table_id: UUID
    kind: Literal["primary_key", "unique", "foreign_key", "check"]
    column_ids: list[UUID]
    name: str | None = None
    expression: Expression | None = None
    location: SourceLocation | None = None


class Relation(Contract):
    constraint_id: UUID
    source_table_id: UUID
    target_table_id: UUID
    column_pairs: list[tuple[UUID, UUID]]
    match: str
    on_update: str
    on_delete: str
    deferrable: bool
    initially_deferred: bool


class ParsedSchema(Contract):
    schema_version_id: UUID
    tables: list[Table]
    columns: list[Column]
    constraints: list[Constraint]
    relations: list[Relation]
    diagnostics: list[Diagnostic]


class SchemaAnalysis(ParsedSchema):
    contract_version: Literal[1]
    analysis_profile: AnalysisProfile
    supported: bool

    @model_validator(mode="after")
    def diagnostics_match_result(self):
        errors = any(item.severity == "error" for item in self.diagnostics)
        if (self.supported and errors) or (not self.supported and not self.diagnostics):
            raise ValueError("supported must agree with error diagnostics")
        return self


def canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class Checkpoint(Contract):
    contract_version: Literal[1]
    schema_version_id: UUID
    manifest_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    analysis_profile: AnalysisProfile
    parsed: ParsedSchema
    model_hash: str = Field(pattern=r"^[0-9a-f]{64}$")

    def valid_for(self, bundle: DdlBundle, profile: AnalysisProfile) -> bool:
        return (self.schema_version_id == bundle.schema_version_id
                and self.manifest_hash == bundle.manifest_hash
                and self.analysis_profile == profile
                and self.parsed.schema_version_id == bundle.schema_version_id
                and self.model_hash == hashlib.sha256(canonical_json(self.parsed.model_dump(mode="json"))).hexdigest())


class DdlParser(Protocol):
    def parse(self, bundle: DdlBundle, profile: AnalysisProfile) -> ParsedSchema: ...


class DdlSupport(Protocol):
    def diagnose(self, parsed: ParsedSchema, profile: AnalysisProfile) -> SchemaAnalysis: ...


class DdlAnalyzer(Protocol):
    def analyze(self, bundle: DdlBundle, profile: AnalysisProfile) -> SchemaAnalysis: ...


class StagedDdlAnalyzer:
    """Compose parser and support stages while keeping checkpointing outside their ports."""

    def __init__(self, parser: DdlParser, support: DdlSupport,
                 save: Callable[[Checkpoint], None], resume: Checkpoint | None = None):
        self.parser, self.support, self.save, self.resume = parser, support, save, resume

    def analyze(self, bundle: DdlBundle, profile: AnalysisProfile) -> SchemaAnalysis:
        if self.resume is not None and self.resume.valid_for(bundle, profile):
            parsed = self.resume.parsed
        else:
            parsed = self.parser.parse(bundle, profile)
            if parsed.schema_version_id != bundle.schema_version_id:
                raise ValueError("parser returned a different schema version")
            model_hash = hashlib.sha256(canonical_json(parsed.model_dump(mode="json"))).hexdigest()
            self.save(Checkpoint(contract_version=1, schema_version_id=bundle.schema_version_id,
                                 manifest_hash=bundle.manifest_hash, analysis_profile=profile,
                                 parsed=parsed, model_hash=model_hash))
        result = self.support.diagnose(parsed, profile)
        if result.schema_version_id != bundle.schema_version_id or result.analysis_profile != profile:
            raise ValueError("analysis does not match its input")
        return result
