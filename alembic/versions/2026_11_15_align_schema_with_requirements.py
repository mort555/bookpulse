"""align schema with data model requirements

Revision ID: 7e4c91a2d8b6
Revises: f80864e21a3e
Create Date: 2026-11-15

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e4c91a2d8b6"
down_revision: str | Sequence[str] | None = "f80864e21a3e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    supplier_count = bind.scalar(sa.text("SELECT count(*) FROM suppliers"))
    if supplier_count:
        raise RuntimeError(
            "Cannot add required suppliers.email while suppliers exist. "
            "Provide email addresses before applying this migration."
        )

    op.add_column(
        "suppliers",
        sa.Column("email", sa.String(length=255), nullable=False),
    )

    op.execute("UPDATE users SET email = lower(email)")
    op.create_check_constraint(
        "check_user_email_lowercase",
        "users",
        "email = lower(email)",
    )
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        server_default=sa.true(),
    )
    op.alter_column(
        "users",
        "weekly_report",
        existing_type=sa.Boolean(),
        server_default=sa.true(),
    )

    op.create_foreign_key(
        "products_category_id_fkey",
        "products",
        "categories",
        ["category_id"],
        ["id"],
    )
    op.create_check_constraint(
        "check_product_rating",
        "products",
        "rating BETWEEN 1 AND 5",
    )

    op.drop_constraint(
        "market_prices_scrape_run_id_fkey",
        "market_prices",
        type_="foreignkey",
    )
    op.alter_column(
        "market_prices",
        "scrape_run_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_foreign_key(
        "market_prices_scrape_run_id_fkey",
        "market_prices",
        "scrape_runs",
        ["scrape_run_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_constraint(
        "supplier_price_uploads_created_by_fkey",
        "supplier_price_uploads",
        type_="foreignkey",
    )
    op.drop_constraint(
        "supplier_price_uploads_supplier_id_key",
        "supplier_price_uploads",
        type_="unique",
    )
    op.drop_constraint(
        "supplier_price_uploads_file_hash_key",
        "supplier_price_uploads",
        type_="unique",
    )
    op.create_foreign_key(
        "supplier_price_uploads_created_by_fkey",
        "supplier_price_uploads",
        "users",
        ["created_by"],
        ["id"],
    )
    op.create_unique_constraint(
        "uq_supplier_price_upload_supplier_hash",
        "supplier_price_uploads",
        ["supplier_id", "file_hash"],
    )

    op.alter_column(
        "supplier_prices",
        "valid_from",
        existing_type=sa.DateTime(),
        type_=sa.Date(),
        postgresql_using="valid_from::date",
    )
    op.create_unique_constraint(
        "uq_supplier_product_valid_from",
        "supplier_prices",
        ["supplier_id", "product_id", "valid_from"],
    )

    op.alter_column(
        "alert_rules",
        "product_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "alert_rules",
        "category_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_check_constraint(
        "check_alert_rule_one_target",
        "alert_rules",
        "(product_id IS NOT NULL AND category_id IS NULL) OR "
        "(product_id IS NULL AND category_id IS NOT NULL)",
    )
    op.create_check_constraint(
        "check_alert_rule_threshold",
        "alert_rules",
        "(type = 'out_of_stock' AND threshold IS NULL) OR "
        "(type IN ('market_price_drop', 'margin_below') "
        "AND threshold IS NOT NULL)",
    )

    op.execute(
        'CREATE TYPE "ReportStatusEnum_v2" '
        "AS ENUM ('queued', 'running', 'done', 'failed')"
    )
    op.execute(
        'ALTER TABLE reports ALTER COLUMN status TYPE "ReportStatusEnum_v2" '
        'USING status::text::"ReportStatusEnum_v2"'
    )
    op.execute('DROP TYPE "ReportStatusEnum"')
    op.execute('ALTER TYPE "ReportStatusEnum_v2" RENAME TO "ReportStatusEnum"')
    op.alter_column(
        "reports",
        "created_at",
        existing_type=sa.String(length=150),
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at::timestamptz",
    )
    op.alter_column(
        "reports",
        "expires_at",
        existing_type=sa.String(length=150),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="expires_at::timestamptz",
    )

    op.drop_constraint(
        "audit_logs_user_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )
    op.alter_column(
        "audit_logs",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "audit_logs",
        "created_at",
        existing_type=sa.String(length=150),
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at::timestamptz",
    )
    op.create_foreign_key(
        "audit_logs_user_id_fkey",
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    bind = op.get_bind()
    completed_reports = bind.scalar(
        sa.text("SELECT count(*) FROM reports WHERE status = 'done'")
    )
    if completed_reports:
        raise RuntimeError(
            "Cannot downgrade report statuses while reports with status 'done' "
            "exist; update or remove them first."
        )

    op.drop_constraint(
        "audit_logs_user_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )
    op.alter_column(
        "audit_logs",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.String(length=150),
        postgresql_using="created_at::text",
    )
    op.alter_column(
        "audit_logs",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "audit_logs_user_id_fkey",
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
    )

    op.alter_column(
        "reports",
        "expires_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.String(length=150),
        existing_nullable=True,
        postgresql_using="expires_at::text",
    )
    op.alter_column(
        "reports",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.String(length=150),
        postgresql_using="created_at::text",
    )
    op.execute(
        "CREATE TYPE \"ReportStatusEnum_v1\" AS ENUM ('queued', 'running', 'failed')"
    )
    op.execute(
        'ALTER TABLE reports ALTER COLUMN status TYPE "ReportStatusEnum_v1" '
        'USING status::text::"ReportStatusEnum_v1"'
    )
    op.execute('DROP TYPE "ReportStatusEnum"')
    op.execute('ALTER TYPE "ReportStatusEnum_v1" RENAME TO "ReportStatusEnum"')

    op.drop_constraint(
        "check_alert_rule_threshold",
        "alert_rules",
        type_="check",
    )
    op.drop_constraint(
        "check_alert_rule_one_target",
        "alert_rules",
        type_="check",
    )
    op.alter_column(
        "alert_rules",
        "category_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "alert_rules",
        "product_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_constraint(
        "uq_supplier_product_valid_from",
        "supplier_prices",
        type_="unique",
    )
    op.alter_column(
        "supplier_prices",
        "valid_from",
        existing_type=sa.Date(),
        type_=sa.DateTime(),
        postgresql_using="valid_from::timestamp",
    )

    op.drop_constraint(
        "uq_supplier_price_upload_supplier_hash",
        "supplier_price_uploads",
        type_="unique",
    )
    op.drop_constraint(
        "supplier_price_uploads_created_by_fkey",
        "supplier_price_uploads",
        type_="foreignkey",
    )
    op.create_unique_constraint(
        "supplier_price_uploads_supplier_id_key",
        "supplier_price_uploads",
        ["supplier_id"],
    )
    op.create_unique_constraint(
        "supplier_price_uploads_file_hash_key",
        "supplier_price_uploads",
        ["file_hash"],
    )
    op.create_foreign_key(
        "supplier_price_uploads_created_by_fkey",
        "supplier_price_uploads",
        "suppliers",
        ["created_by"],
        ["id"],
    )

    op.drop_constraint(
        "market_prices_scrape_run_id_fkey",
        "market_prices",
        type_="foreignkey",
    )
    op.alter_column(
        "market_prices",
        "scrape_run_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "market_prices_scrape_run_id_fkey",
        "market_prices",
        "scrape_runs",
        ["scrape_run_id"],
        ["id"],
    )

    op.drop_constraint("check_product_rating", "products", type_="check")
    op.drop_constraint(
        "products_category_id_fkey",
        "products",
        type_="foreignkey",
    )

    op.drop_column("suppliers", "email")
    op.drop_constraint("check_user_email_lowercase", "users", type_="check")
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        server_default=None,
    )
    op.alter_column(
        "users",
        "weekly_report",
        existing_type=sa.Boolean(),
        server_default=None,
    )
