from sqlalchemy.orm import Session

from ...config import Config
from .create_test_user import create_test_user


logger = __import__("logging").getLogger(__name__)


def setup_database(db: "Session"):
    logger.info("Setting up database")
    if Config.APP_ENV == "local":
        create_test_user(db)
    logger.info("Database setup complete")
