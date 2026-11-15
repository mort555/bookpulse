from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Посилання на таблицю products (у множині)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )

    # Згідно зі специфікацією: FK та nullable=True
    scrape_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("scrape_runs.id", ondelete="SET NULL"), nullable=True
    )

    price_incl_tax: Mapped[float] = mapped_column(Float, nullable=False)
    price_excl_tax: Mapped[float] = mapped_column(Float, nullable=False)
    tax: Mapped[float] = mapped_column(Float, nullable=False)

    in_stock: Mapped[int] = mapped_column(Integer, nullable=False)

    # Дата/час скрапування
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )

    # Правильне оформлення перевірки (check constraint) для залишку >= 0
    __table_args__ = (
        CheckConstraint("in_stock >= 0", name="check_in_stock_not_negative"),
    )
