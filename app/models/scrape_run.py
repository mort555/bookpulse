from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    engine: Mapped[str] = mapped_column(
        Enum("bs4", "scrapy", name="scrape_engine_enum"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Enum("queued", "running", "done", "failed", name="scrape_status_enum"),
        nullable=False,
    )

    trigger: Mapped[str] = mapped_column(
        Enum("manual", "schedule", "cli", name="scrape_trigger_enum"),
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    items_scraped: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    items_changed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    errors_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
