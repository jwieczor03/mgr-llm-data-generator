"""Persist discoveries, proposals and immutable review decisions."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = '0004_relations'
down_revision = '0003_ddl_versions'
branch_labels = None
depends_on = None


def upgrade():
    uid = sa.Uuid()
    op.add_column('projects', sa.Column('requirements_revision', sa.BigInteger(), nullable=False, server_default='0'), schema='app')
    op.create_table('relation_discoveries',
        sa.Column('id', uid, primary_key=True), sa.Column('project_id', uid, nullable=False),
        sa.Column('schema_version_id', uid, nullable=False), sa.Column('interpretation_id', uid, nullable=False),
        sa.Column('request_id', uid, nullable=False), sa.Column('status', sa.Text(), nullable=False),
        sa.Column('deadline', sa.DateTime(timezone=True)), sa.Column('error_code', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id', 'schema_version_id'], ['app.schema_versions.project_id', 'app.schema_versions.id']),
        sa.ForeignKeyConstraint(['interpretation_id'], ['app.schema_interpretations.id']),
        sa.UniqueConstraint('project_id', 'schema_version_id', 'request_id'),
        sa.CheckConstraint("status IN ('PENDING','RUNNING','SUCCEEDED','FAILED')"), schema='app')
    op.create_table('relation_proposals',
        sa.Column('id', uid, primary_key=True), sa.Column('project_id', uid, nullable=False),
        sa.Column('schema_version_id', uid, nullable=False), sa.Column('interpretation_id', uid, nullable=False),
        sa.Column('discovery_id', uid, sa.ForeignKey('app.relation_discoveries.id')),
        sa.Column('source', sa.Text(), nullable=False), sa.Column('revision', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('definition', JSONB, nullable=False), sa.Column('invalid_reason', sa.Text()),
        sa.ForeignKeyConstraint(['project_id', 'schema_version_id'], ['app.schema_versions.project_id', 'app.schema_versions.id']),
        sa.ForeignKeyConstraint(['interpretation_id'], ['app.schema_interpretations.id']),
        sa.CheckConstraint("source IN ('MODEL_PROPOSAL','CARRIED_FORWARD')"), schema='app')
    op.create_table('relation_decisions',
        sa.Column('id', uid, primary_key=True), sa.Column('proposal_id', uid, sa.ForeignKey('app.relation_proposals.id'), nullable=False, unique=True),
        sa.Column('proposal_revision', sa.Integer(), nullable=False), sa.Column('decision', sa.Text(), nullable=False),
        sa.Column('reference_required', sa.Boolean()), sa.Column('owner_subject', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint("(decision='APPROVE' AND reference_required IS NOT NULL) OR (decision='REJECT' AND reference_required IS NULL)"), schema='app')


def downgrade():
    for table in ('relation_decisions', 'relation_proposals', 'relation_discoveries'):
        op.drop_table(table, schema='app')
    op.drop_column('projects', 'requirements_revision', schema='app')
