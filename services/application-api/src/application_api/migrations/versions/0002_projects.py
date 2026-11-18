"""Create projects with a globally unique backend-computed name key."""
import sqlalchemy as sa
from alembic import op

revision = "0002_projects"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_subject", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("name_key", sa.Text(collation="C"), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name_key", name="uq_projects_name_key"),
        sa.CheckConstraint("char_length(name) BETWEEN 1 AND 100", name="ck_projects_name_length"),
        sa.CheckConstraint("description IS NULL OR char_length(description) <= 2000", name="ck_projects_description_length"),
        schema="app",
    )


def downgrade():
    op.drop_table("projects", schema="app")
