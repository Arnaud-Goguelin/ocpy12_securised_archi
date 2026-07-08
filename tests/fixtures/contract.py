from decimal import Decimal

import pytest

from crm_epic_events.services import ContractCreateInput
from tests.factories import (
    ContractDBFactory,
)


@pytest.fixture
def contract(db_session):
    return ContractDBFactory()


@pytest.fixture
def signed_contract():
    return ContractDBFactory(status=True)


@pytest.fixture
def unsigned_contract():
    return ContractDBFactory(status=False)


@pytest.fixture
def contract_create_data(signed_contract):
    return ContractCreateInput(
        customer_id=signed_contract.customer_id,
        salesperson_id=signed_contract.salesperson_id,
        status=signed_contract.status,
        total_amount=Decimal("1000"),
        remaining_amount=Decimal("500"),
    )
