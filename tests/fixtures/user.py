import pytest

from crm_epic_events.permissions import Roles
from crm_epic_events.services import UserRegisterInput
from tests.factories import (
    SECURED_RAW_PASSWORD,
    UserDBFactory,
    fake,
)


@pytest.fixture
def manager(db_session):
    return UserDBFactory(role=Roles.MANAGER)


@pytest.fixture
def salesperson(db_session):
    return UserDBFactory(role=Roles.SALES)


@pytest.fixture
def support(db_session):
    return UserDBFactory(role=Roles.SUPPORT)


@pytest.fixture
def register_data() -> UserRegisterInput:
    return UserRegisterInput(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
        password=SECURED_RAW_PASSWORD,
    )
