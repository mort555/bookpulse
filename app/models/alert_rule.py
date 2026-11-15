from sqlalchemy import CheckConstraint, Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"
    __table_args__ = (
        CheckConstraint(
            "(product_id IS NOT NULL AND category_id IS NULL) OR "
            "(product_id IS NULL AND category_id IS NOT NULL)",
            name="check_alert_rule_one_target",
        ),
        CheckConstraint(
            "(type = 'out_of_stock' AND threshold IS NULL) OR "
            "(type IN ('market_price_drop', 'margin_below') "
            "AND threshold IS NOT NULL)",
            name="check_alert_rule_threshold",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    type: Mapped[Enum] = mapped_column(
        Enum(
            "market_price_drop",
            "margin_below",
            "out_of_stock",
            name="alert_rule_type_enum",
        ),
        nullable=False,
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )
    threshold: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
