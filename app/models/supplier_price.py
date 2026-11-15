from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SupplierPrice(Base):
    __tablename__ = "supplier_prices"
    __table_args__ = (
        Index(
            "ix_supplier_prices_product_valid_from",
            "product_id",
            text("valid_from DESC"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    supplier_price_upload_id: Mapped[int] = mapped_column(
        ForeignKey("supplier_price_uploads.id", ondelete="CASCADE"), nullable=False
    )
    purchase_price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
