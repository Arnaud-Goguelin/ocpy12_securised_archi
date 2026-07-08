import pytest

from crm_epic_events.services import CustomerCreateInput
from tests.factories import (
    VAT_NUMBER,
    CustomerDBFactory,
    fake,
)


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
