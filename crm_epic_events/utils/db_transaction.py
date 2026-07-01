import logging

from contextlib import contextmanager
from typing import TYPE_CHECKING

from sqlalchemy.exc import SQLAlchemyError


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@contextmanager
def db_transaction(db: "Session", operation: str = "database operation"):
    """
    Sync context manager wrapping a DB transaction with automatic commit on success
    and rollback on any error.

    Pattern:
        with db_transaction(self.db, "Creating user"):
            ...

    On success:  commits the transaction.
    On SQLAlchemyError: rolls back, logs, and re-raises.
    On any other Exception: rolls back and re-raises (caller's error handling applies).
    """
    try:
        yield
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        logger.error(f"SQLAlchemy error during {operation}: {error}")
        raise
    except Exception:
        db.rollback()
        raise
