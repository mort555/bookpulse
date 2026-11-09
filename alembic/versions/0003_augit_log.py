"""audit_log

Revision ID: 0003_audit_log
Revises: 0002_indexes_and_trgm
Create Date: 2026-11-07 23:59:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_audit_log"
down_revision: str | None = "0002_indexes_and_trgm"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Створення таблиці audit_logs для відстеження системних дій / змін
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=150), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"], unique=False)
    op.create_index(
        "idx_audit_logs_user_action",
        "audit_logs",
        ["user_id", "action"],
        unique=False,
    )


def downgrade() -> None:
    # Видалення індексів та таблиці audit_logs у зворотному порядку
    op.drop_index("idx_audit_logs_user_action", table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
