"""init

Revision ID: ef0096e24580
Revises: 
Create Date: 2026-11-09 12:25:35.055725

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = 'ef0096e24580'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
