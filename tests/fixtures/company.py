import pytest

from crm_epic_events.services import CompanyCreateInput
from tests.factories import (
    VAT_NUMBER,
    CompanyDBFactory,
    fake,
)


@pytest.fixture
def company(db_session):
    return CompanyDBFactory()


@pytest.fixture
def company_create_data(signed_contract):
    return CompanyCreateInput(
        vat_number=VAT_NUMBER,
        name=fake.company(),
    )
