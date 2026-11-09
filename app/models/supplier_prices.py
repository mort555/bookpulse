from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class supplier_prices(Base):
    __tablename__ = "supplier_prices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    supplier_id: Mapped[str] = mapped_column(
        String(150), ForeignKey("suppliers.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    import_id: Mapped[int] = mapped_column(
        ForeignKey("imports.id", ondelete="CASCADE"), nullable=False
    )
    purchase_price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
