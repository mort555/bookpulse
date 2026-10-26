import argparse
import sys

import structlog
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.infra.database.session import engine

logger = structlog.get_logger()


def seed() -> int:
    """Check database connectivity before running seed operations."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("seed_database_connection_failed")
        return 1

    logger.info("seed_completed", message="Database connection is available.")
    return 0


def main() -> int:
    """Parse CLI arguments and run the requested command."""
    parser = argparse.ArgumentParser(description="BookPulse CLI")
    parser.add_argument(
        "command",
        choices=["seed"],
        help="Command to execute",
    )
    args = parser.parse_args()

    if args.command == "seed":
        return seed()

    return 0


if __name__ == "__main__":
    sys.exit(main())
