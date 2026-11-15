from enum import StrEnum, auto


class Roles(StrEnum):
    """User roles."""

    ADMIN = auto()
    MANAGER = auto()
    VIEWER = auto()
