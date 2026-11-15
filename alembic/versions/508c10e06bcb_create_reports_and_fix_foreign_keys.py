"""create reports and fix foreign keys

Revision ID: 508c10e06bcb
Revises: e71974702256
Create Date: 2026-11-15 02:50:09.971528

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "508c10e06bcb"
down_revision: str | Sequence[str] | None = "e71974702256"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Снимаем внешние ключи со ВСЕХ таблиц, ссылающихся на users.id
    op.drop_constraint("scrape_runs_created_by_fkey", "scrape_runs", type_="foreignkey")
    op.drop_constraint("alert_rules_user_id_fkey", "alert_rules", type_="foreignkey")

    # 2. Меняем тип `id` в таблице `users` на INTEGER
    op.alter_column(
        "users",
        "id",
        existing_type=sa.VARCHAR(length=150),
        type_=sa.Integer(),
        existing_nullable=False,
        autoincrement=True,
        postgresql_using="id::integer",
    )

    # 3. Меняем тип `created_by` в таблице `scrape_runs` на INTEGER
    op.alter_column(
        "scrape_runs",
        "created_by",
        existing_type=sa.VARCHAR(length=150),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="created_by::integer",
    )

    # 4. Меняем тип `user_id` в таблице `alert_rules` на INTEGER
    op.alter_column(
        "alert_rules",
        "user_id",
        existing_type=sa.VARCHAR(length=150),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="user_id::integer",
    )

    # 5. Возвращаем внешние ключи обратно (теперь все поля типа INTEGER!)
    op.create_foreign_key(
        "scrape_runs_created_by_fkey",
        "scrape_runs",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "alert_rules_user_id_fkey", "alert_rules", "users", ["user_id"], ["id"]
    )

    # 6. Создаем новую таблицу `reports`
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "type", sa.Enum("analysis", "summary", name="ReportType"), nullable=False
        ),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "failed", name="ReportStatusEnum"),
            nullable=False,
        ),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.String(length=150), nullable=False),
        sa.Column("expires_at", sa.String(length=150), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reports_id"), "reports", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_reports_id"), table_name="reports")
    op.drop_table("reports")

    op.drop_constraint("alert_rules_user_id_fkey", "alert_rules", type_="foreignkey")
    op.drop_constraint("scrape_runs_created_by_fkey", "scrape_runs", type_="foreignkey")

    op.alter_column(
        "alert_rules",
        "user_id",
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(length=150),
        existing_nullable=False,
        postgresql_using="user_id::varchar",
    )

    op.alter_column(
        "scrape_runs",
        "created_by",
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(length=150),
        existing_nullable=True,
        postgresql_using="created_by::varchar",
    )

    op.alter_column(
        "users",
        "id",
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(length=150),
        existing_nullable=False,
        autoincrement=True,
        postgresql_using="id::varchar",
    )

    op.create_foreign_key(
        "alert_rules_user_id_fkey", "alert_rules", "users", ["user_id"], ["id"]
    )
    op.create_foreign_key(
        "scrape_runs_created_by_fkey",
        "scrape_runs",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )
