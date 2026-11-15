from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SupplierPrice(Base):
    __tablename__ = "supplier_prices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("supplier.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    supplier_price_upload_id: Mapped[int] = mapped_column(
        ForeignKey("supplier_price_upload.id", ondelete="CASCADE"), nullable=False
    )
    purchase_price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
