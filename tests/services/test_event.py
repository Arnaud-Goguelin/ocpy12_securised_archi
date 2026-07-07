import uuid

import pytest

from crm_epic_events.errors import ContractNotFoundError, ContractNotSignedError
from crm_epic_events.services.event.schemas import EventCreateInput, EventUpdateInput
from crm_epic_events.services.event.service import EventService
from crm_epic_events.utils.constants import Roles
from tests.factories import EventDBFactory, UserDBFactory, fake


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_returns_all_events(self, db_session):
        # cannot use create_batch from EventDBFactory object because it would link each event to the same contract
        # whereas, relationship is one to one with contract
        for _ in range(3):
            EventDBFactory()
        result = EventService.get_all(db_session)
        assert len(result) == 3

    def test_returns_empty_list(self, db_session):
        result = EventService.get_all(db_session)
        assert result == []


# ── get_all_without_support ───────────────────────────────────────────────────


class TestGetAllWithoutSupport:
    def test_returns_only_events_without_support(self, db_session):
        support = UserDBFactory(role=Roles.SUPPORT)
        EventDBFactory(support_id=None)
        EventDBFactory(support_id=support.id)
        result = EventService.get_all_without_support(db_session)
        assert len(result) == 1
        assert result[0].support_id is None

    def test_returns_empty_when_all_have_support(self, db_session):
        support = UserDBFactory(role=Roles.SUPPORT)
        EventDBFactory(support_id=support.id)
        result = EventService.get_all_without_support(db_session)
        assert result == []


# ── get_all_by_support ────────────────────────────────────────────────────────


class TestGetAllBySupport:
    def test_returns_events_for_support_user(self, db_session):
        support = UserDBFactory(role=Roles.SUPPORT)
        EventDBFactory(support_id=support.id)
        EventDBFactory(support_id=None)  # autre event sans support
        result = EventService.get_all_by_support(support, db_session)
        assert len(result) == 1
        assert result[0].support_id == support.id

    def test_returns_empty_list_when_no_events(self, db_session):
        support = UserDBFactory(role=Roles.SUPPORT)
        result = EventService.get_all_by_support(support, db_session)
        assert result == []


# ── get_by_id ─────────────────────────────────────────────────────────────────


class TestGetById:
    def test_returns_event_when_found(self, db_session):
        event = EventDBFactory()
        result = EventService.get_by_id(event.id, db_session)
        assert result is not None
        assert result.id == event.id

    def test_returns_none_when_not_found(self, db_session):
        result = EventService.get_by_id(uuid.uuid4(), db_session)
        assert result is None


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def test_creates_and_returns_event(self, db_session, event_create_data):
        event = EventService.create(event_create_data, db_session)
        assert event.id is not None
        assert event.location == event_create_data.location
        assert event.attendees == event_create_data.attendees

    def test_event_is_persisted(self, db_session, event_create_data):
        event = EventService.create(event_create_data, db_session)
        result = EventService.get_by_id(event.id, db_session)
        assert result is not None

    def test_raises_if_contract_not_found(self, db_session, event_create_data):
        event_create_data = event_create_data.model_copy(update={"contract_id": uuid.uuid4()})
        with pytest.raises(ContractNotFoundError):
            EventService.create(event_create_data, db_session)

    def test_raises_if_contract_not_signed(self, db_session, unsigned_contract):
        data = EventCreateInput(
            contract_id=unsigned_contract.id,
            customer_id=unsigned_contract.customer_id,
            support_id=None,
            start_date=fake.date_time_this_year(tzinfo=__import__("datetime").timezone.utc),
            end_date=fake.future_datetime(tzinfo=__import__("datetime").timezone.utc),
            location=fake.city(),
            attendees=fake.pyint(min_value=1, max_value=500),
            notes=None,
        )
        with pytest.raises(ContractNotSignedError):
            EventService.create(data, db_session)

    def test_support_id_is_optional(self, db_session, event_create_data):
        event = EventService.create(event_create_data, db_session)
        assert event.support_id is None

    def test_notes_is_optional(self, db_session, event_create_data):
        event = EventService.create(event_create_data, db_session)
        assert event.notes is None


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_updates_location(self, db_session):
        event = EventDBFactory(location="Paris")
        data = EventUpdateInput(location="Lyon")
        updated = EventService.update(event, data, db_session)
        assert updated.location == "Lyon"

    def test_updates_attendees(self, db_session):
        event = EventDBFactory(attendees=50)
        data = EventUpdateInput(attendees=200)
        updated = EventService.update(event, data, db_session)
        assert updated.attendees == 200

    def test_partial_update_does_not_affect_other_fields(self, db_session):
        event = EventDBFactory(location="Paris", attendees=50)
        data = EventUpdateInput(location="Lyon")
        updated = EventService.update(event, data, db_session)
        assert updated.attendees == 50

    def test_assign_support_on_update(self, db_session):
        support = UserDBFactory(role=Roles.SUPPORT)
        event = EventDBFactory(support_id=None)
        data = EventUpdateInput(support_id=support.id)
        updated = EventService.update(event, data, db_session)
        assert updated.support_id == support.id


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_deletes_event(self, db_session):
        event = EventDBFactory()
        event_id = event.id
        EventService.delete(event, db_session)
        assert EventService.get_by_id(event_id, db_session) is None

    def test_delete_returns_none(self, db_session):
        event = EventDBFactory()
        result = EventService.delete(event, db_session)
        assert result is None
