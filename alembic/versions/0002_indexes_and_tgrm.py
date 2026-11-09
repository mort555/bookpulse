"""indexes_and_trgm

Revision ID: 0002_indexes_and_trgm
Revises: 125b8245a52d
Create Date: 2026-11-07 23:55:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_indexes_and_trgm"
down_revision: str | None = "125b8245a52d"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # 1. Підключення розширення pg_trgm для швидкого текстового пошуку
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 2. Створення індексів
    # GIN-індекс для швидкого ILIKE пошуку за назвою товару (title)
    op.execute(
        "CREATE INDEX idx_products_title_trgm ON products USING gin"
        " (title gin_trgm_ops);"
    )

    # Індекс для швидкого отримання останньої ціни товару за датою у market_prices
    op.create_index(
        "idx_market_prices_product_date",
        "market_prices",
        ["product_id", "scraped_at"],
        unique=False,
    )

    # Індекс для фільтрації активних правил сповіщень
    op.create_index(
        "idx_alert_rules_user_active",
        "alert_rules",
        ["user_id", "is_active"],
        unique=False,
    )


def downgrade() -> None:
    # Видалення індексів у зворотному порядку
    op.drop_index("idx_alert_rules_user_active", table_name="alert_rules")
    op.drop_index("idx_market_prices_product_date", table_name="market_prices")
    op.execute("DROP INDEX IF EXISTS idx_products_title_trgm;")

    # Видалення розширення pg_trgm
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
