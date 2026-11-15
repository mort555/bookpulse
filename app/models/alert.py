from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index(
            "ix_alerts_pending_notified_at",
            "notified_at",
            postgresql_where=text("notified_at IS NULL"),
        ),
        Index(
            "ix_alerts_rule_product_created_at",
            "rule_id",
            "product_id",
            text("created_at DESC"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("alert_rules.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    # JSONB у Python мапиться на dict (або dict | list), а не str
    payload: Mapped[dict[str, Any] | list[Any]] = mapped_column(JSONB, nullable=False)

    # Python-тип datetime, а не DateTime
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
