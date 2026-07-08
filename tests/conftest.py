from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from crm_epic_events.models.database import Base
from crm_epic_events.services import ContractCreateInput, CustomerCreateInput, EventCreateInput, UserRegisterInput
from crm_epic_events.services.authentication.service import AuthTokensService
from crm_epic_events.utils import Roles
from tests.factories import (
    SECURED_RAW_PASSWORD,
    VAT_NUMBER,
    CompanyDBFactory,
    ContractDBFactory,
    CustomerDBFactory,
    EventDBFactory,
    UserDBFactory,
    UserFactory,
    fake,
)


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


# ===== auth fixtures =====


@pytest.fixture
def access_token():
    def _make(user, expired: bool = False) -> str:
        with patch("crm_epic_events.services.authentication.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, tzinfo=UTC) if expired else datetime.now(UTC)
            token = AuthTokensService.generate_access_token(user)
            return token

    return _make


@pytest.fixture
def refresh_token():
    def _make(user, expired: bool = False) -> str:
        with patch("crm_epic_events.services.authentication.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, tzinfo=UTC) if expired else datetime.now(UTC)
            token = AuthTokensService.generate_refresh_token(user)
            return token

    return _make


@pytest.fixture(autouse=True)
def clear_tokens():
    """Ensure no leftover token file between tests."""
    AuthTokensService.clear_tokens()
    yield
    AuthTokensService.clear_tokens()


# ===== Customer fixtures =====


@pytest.fixture
def customer(db_session):
    return CustomerDBFactory()


@pytest.fixture
def customer_create_data(salesperson):
    return CustomerCreateInput(
        salesperson_id=salesperson.id,
        vat_number=VAT_NUMBER,
        company_name=fake.company(),
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        phone=fake.phone_number(),
    )


# ===== User fixtures =====


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


# ===== Contract fixtures =====


@pytest.fixture
def contract(db_session):
    return ContractDBFactory()


@pytest.fixture
def contract_create_data(signed_contract):
    return ContractCreateInput(
        customer_id=signed_contract.customer_id,
        salesperson_id=signed_contract.salesperson_id,
        status=signed_contract.status,
        total_amount=Decimal("1000"),
        remaining_amount=Decimal("500"),
    )


# === Event fixtures ===


@pytest.fixture
def signed_contract():
    return ContractDBFactory(status=True)


@pytest.fixture
def unsigned_contract():
    return ContractDBFactory(status=False)


@pytest.fixture
def event_create_data(signed_contract):
    return EventCreateInput(
        contract_id=signed_contract.id,
        customer_id=signed_contract.customer_id,
        support_id=None,
        start_date=fake.date_time_this_year(tzinfo=__import__("datetime").timezone.utc),
        end_date=fake.future_datetime(tzinfo=__import__("datetime").timezone.utc),
        location=fake.city(),
        attendees=fake.pyint(min_value=1, max_value=500),
        notes=None,
    )
