from unittest.mock import MagicMock

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from crm_epic_events.models.database import Base
from tests.factories import (
    CompanyDBFactory,
    ContractDBFactory,
    CustomerDBFactory,
    EventDBFactory,
    UserDBFactory,
    UserFactory,
)


pytest_plugins = [
    "tests.fixtures.user",
    "tests.fixtures.customer",
    "tests.fixtures.contract",
    "tests.fixtures.event",
    "tests.fixtures.company",
    "tests.fixtures.auth",
]


# ===== db fixtures to test persistence (services and models) in DB =====
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def setup_db_factories(db_session):
    UserDBFactory._meta.sqlalchemy_session = db_session
    CompanyDBFactory._meta.sqlalchemy_session = db_session
    CustomerDBFactory._meta.sqlalchemy_session = db_session
    ContractDBFactory._meta.sqlalchemy_session = db_session
    EventDBFactory._meta.sqlalchemy_session = db_session


# ===== db mock to test without persistence (controllers) in DB =====


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def user():
    return UserFactory()
