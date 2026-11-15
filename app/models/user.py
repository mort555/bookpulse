from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Integer,
    String,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.enum import Roles
from app.database.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="check_user_email_lowercase"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Roles] = mapped_column(
        Enum(Roles, name="user_role_enum"), nullable=False, default=Roles.VIEWER
    )  # Example role field
    weekly_report: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )  # Weekly report subscription
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )  # Store as datetime for simplicity

    @validates("email")
    def normalize_email(self, key: str, value: str) -> str:
        return value.lower()
