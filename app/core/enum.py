from enum import StrEnum, auto


class Roles(StrEnum):
    """User roles."""

    ADMIN = auto()
    MANEGER = auto()
    VIEWER = auto()
