import pytest

from crm_epic_events.services import EventCreateInput
from tests.factories import (
    EventDBFactory,
    fake,
)


@pytest.fixture
def event():
    return EventDBFactory()


@pytest.fixture
def event_create_data(signed_contract, support):
    return EventCreateInput(
        contract_id=signed_contract.id,
        customer_id=signed_contract.customer_id,
        support_id=support.id,
        start_date=fake.date_time_this_year(tzinfo=__import__("datetime").timezone.utc),
        end_date=fake.future_datetime(tzinfo=__import__("datetime").timezone.utc),
        location=fake.city(),
        attendees=fake.pyint(min_value=1, max_value=500),
        notes=None,
    )
