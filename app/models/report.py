from typing import Any

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    type: Mapped[Enum] = mapped_column(
        Enum("analysis", "summary", name="ReportType"), nullable=False
    )
    params: Mapped[dict[str, Any] | list[Any]] = mapped_column(JSONB, nullable=True)
    status: Mapped[Enum] = mapped_column(
        Enum("queued", "running", "failed", name="ReportStatusEnum"),
        nullable=False,
    )
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[str] = mapped_column(String(150), nullable=False)
    expires_at: Mapped[str | None] = mapped_column(String(150), nullable=True)
