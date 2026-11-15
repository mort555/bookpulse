from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SupplierPriceUpload(Base):
    __tablename__ = "supplier_price_upload"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    suplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("supplier.id"), unique=True, nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(150), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    status: Mapped[Enum] = mapped_column(
        Enum(
            "queued",
            "processing",
            "done",
            "failed",
            name="supplier_price_upload_status_enum",
        ),
        nullable=False,
    )
    rows_total: Mapped[int] = mapped_column(nullable=False)
    rows_ok: Mapped[int] = mapped_column(nullable=False)
    rows_failed: Mapped[int] = mapped_column(nullable=False)
    error_report_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    fail_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("supplier.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
