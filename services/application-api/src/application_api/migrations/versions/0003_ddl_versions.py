"""Persist DDL attempts, their journal, and immutable schema versions."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0003_ddl_versions"
down_revision = "0002_projects"
branch_labels = None
depends_on = None


def upgrade():
    uid = sa.Uuid()
    time = sa.DateTime(timezone=True)
    op.create_table(
        "ddl_attempts",
        sa.Column("id", uid, primary_key=True),
        sa.Column("project_id", uid, sa.ForeignKey("app.projects.id"), nullable=False),
        sa.Column("owner_subject", sa.Text(), nullable=False),
        sa.Column("page_id", uid, nullable=False),
        sa.Column("reservation", JSONB, nullable=False),
        sa.Column("reservation_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("lease_expires_at", time),
        sa.Column("receipt_nonce", sa.Text()),
        sa.Column("receipt_nonce_hash", sa.String(64)),
        sa.Column("launch_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", time),
        sa.Column("execution_epoch", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("checkpoint", JSONB),
        sa.Column("diagnostics", JSONB),
        sa.Column("cleanup_target", sa.Text()),
        sa.Column("created_at", time, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("project_id", "id", name="uq_ddl_attempt_project_id"),
        sa.CheckConstraint("launch_count BETWEEN 0 AND 4", name="ck_ddl_launch_count"),
        schema="app",
    )
    op.create_table(
        "ddl_slot",
        sa.Column("singleton", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", uid, sa.ForeignKey("app.ddl_attempts.id")),
        sa.CheckConstraint("singleton = 1", name="ck_ddl_slot_singleton"),
        schema="app",
    )
    op.execute("INSERT INTO app.ddl_slot (singleton) VALUES (1)")
    op.create_table(
        "ddl_artifact_journal",
        sa.Column("id", uid, primary_key=True),
        sa.Column("attempt_id", uid, sa.ForeignKey("app.ddl_attempts.id"), nullable=False),
        sa.Column("artifact_id", uid, nullable=False, unique=True),
        sa.UniqueConstraint("attempt_id", "artifact_id", name="uq_ddl_journal_attempt_artifact"),
        schema="app",
    )
    op.create_table(
        "ddl_attempt_files",
        sa.Column("id", uid, primary_key=True),
        sa.Column("attempt_id", uid, sa.ForeignKey("app.ddl_attempts.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("name_key", sa.Text(collation="C"), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("artifact_id", uid, nullable=False),
        sa.ForeignKeyConstraint(["attempt_id", "artifact_id"],
                                ["app.ddl_artifact_journal.attempt_id", "app.ddl_artifact_journal.artifact_id"]),
        sa.UniqueConstraint("attempt_id", "position", name="uq_ddl_file_position"),
        sa.UniqueConstraint("attempt_id", "name_key", name="uq_ddl_file_name"),
        sa.CheckConstraint("position >= 0 AND size_bytes >= 0", name="ck_ddl_file_bounds"),
        schema="app",
    )
    op.create_table(
        "schema_versions",
        sa.Column("id", uid, primary_key=True),
        sa.Column("project_id", uid, sa.ForeignKey("app.projects.id"), nullable=False),
        sa.Column("attempt_id", uid, nullable=False, unique=True),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column("manifest_hash", sa.String(64), nullable=False),
        sa.Column("analysis_profile", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("created_at", time, nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["project_id", "attempt_id"], ["app.ddl_attempts.project_id", "app.ddl_attempts.id"]),
        sa.UniqueConstraint("project_id", "revision_no", name="uq_schema_version_revision"),
        sa.UniqueConstraint("project_id", "id", name="uq_schema_version_project_id"),
        sa.CheckConstraint("revision_no > 0", name="ck_schema_version_revision"),
        schema="app",
    )
    op.create_table(
        "schema_interpretations",
        sa.Column("id", uid, primary_key=True),
        sa.Column("project_id", uid, nullable=False),
        sa.Column("schema_version_id", uid, nullable=False),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column("analysis_profile", sa.Text(), nullable=False),
        sa.Column("analysis", JSONB, nullable=False),
        sa.Column("created_at", time, nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["project_id", "schema_version_id"], ["app.schema_versions.project_id", "app.schema_versions.id"]),
        sa.UniqueConstraint("schema_version_id", "revision_no", name="uq_interpretation_revision"),
        schema="app",
    )
    op.add_column("projects", sa.Column("default_schema_version_id", uid), schema="app")
    op.add_column("projects", sa.Column("requirements_review_required", sa.Boolean(), nullable=False,
                                        server_default=sa.false()), schema="app")
    op.create_foreign_key("fk_project_default_schema_version", "projects", "schema_versions",
                          ["id", "default_schema_version_id"], ["project_id", "id"],
                          source_schema="app", referent_schema="app")


def downgrade():
    op.drop_constraint("fk_project_default_schema_version", "projects", schema="app", type_="foreignkey")
    op.drop_column("projects", "requirements_review_required", schema="app")
    op.drop_column("projects", "default_schema_version_id", schema="app")
    for table in ("schema_interpretations", "schema_versions", "ddl_attempt_files",
                  "ddl_artifact_journal", "ddl_slot", "ddl_attempts"):
        op.drop_table(table, schema="app")
