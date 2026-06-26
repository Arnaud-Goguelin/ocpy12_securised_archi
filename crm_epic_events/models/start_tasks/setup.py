from .create_test_user import create_test_user


logger = __import__("logging").getLogger(__name__)


def setup_database():
    logger.info("Setting up database")
    create_test_user()
    logger.info("Database setup complete")
