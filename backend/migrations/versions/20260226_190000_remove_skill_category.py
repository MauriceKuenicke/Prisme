"""remove_skill_category

Revision ID: 003_remove_skill_category
Revises: 002_seed_test_data
Create Date: 2026-02-26 19:00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003_remove_skill_category"
down_revision = "002_seed_test_data"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def upgrade() -> None:
    if _has_column("blocks", "skill_category"):
        with op.batch_alter_table("blocks") as batch_op:
            batch_op.drop_column("skill_category")


def downgrade() -> None:
    if not _has_column("blocks", "skill_category"):
        with op.batch_alter_table("blocks") as batch_op:
            batch_op.add_column(sa.Column("skill_category", sa.String(length=100), nullable=True))
