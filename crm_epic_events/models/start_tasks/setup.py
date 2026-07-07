from sqlalchemy.orm import Session

from .create_test_user import create_test_user


logger = __import__("logging").getLogger(__name__)


def setup_database(db: "Session"):
    logger.info("Setting up database")
    create_test_user(db)
    logger.info("Database setup complete")
