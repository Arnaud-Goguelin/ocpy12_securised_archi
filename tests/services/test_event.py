import uuid

from unittest.mock import MagicMock, patch

from crm_epic_events.models.event import Event
from crm_epic_events.services.event.schemas import EventCreateInput, EventUpdateInput
from crm_epic_events.services.event.service import EventService
from crm_epic_events.utils import Roles
from tests.factories import EventFactory, UserFactory


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_get_all_returns_events(self, mock_db):
        events = EventFactory.build_batch(3)
        with patch.object(Event, "get_all", return_value=events):
            result = EventService.get_all(mock_db)

        assert result == events

    def test_get_all_returns_empty_list(self, mock_db):
        with patch.object(Event, "get_all", return_value=[]):
            result = EventService.get_all(mock_db)

        assert result == []


# ── get_all_without_support ───────────────────────────────────────────────────


class TestGetAllWithoutSupport:
    def test_returns_events_without_support(self, mock_db):
        events = EventFactory.build_batch(2, support_id=None)

        with patch.object(Event, "get_all_without_support", return_value=events):
            result = EventService.get_all_without_support(mock_db)

        assert result == events
        assert all(e.support_id is None for e in result)

    def test_returns_empty_list_when_all_have_support(self, mock_db):
        with patch.object(Event, "get_all_without_support", return_value=[]):
            result = EventService.get_all_without_support(mock_db)

        assert result == []

    def test_calls_model_with_db(self, mock_db):
        with patch.object(Event, "get_all_without_support", return_value=[]) as mock_get:
            EventService.get_all_without_support(mock_db)

        mock_get.assert_called_once_with(mock_db)


# ── get_all_by_support ────────────────────────────────────────────────────────


class TestGetAllBySupport:
    def test_returns_events_for_support_user(self, mock_db):
        support_user = UserFactory(role=Roles.SUPPORT)
        events = EventFactory.build_batch(2, support_id=support_user.id)

        with patch.object(Event, "get_all_by_support", return_value=events):
            result = EventService.get_all_by_support(support_user, mock_db)

        assert result == events

    def test_returns_empty_list_when_no_events(self, mock_db):
        support_user = UserFactory(role=Roles.SUPPORT)

        with patch.object(Event, "get_all_by_support", return_value=[]):
            result = EventService.get_all_by_support(support_user, mock_db)

        assert result == []

    def test_passes_support_id_to_model(self, mock_db):
        support_user = UserFactory(role=Roles.SUPPORT)

        with patch.object(Event, "get_all_by_support", return_value=[]) as mock_get:
            EventService.get_all_by_support(support_user, mock_db)

        mock_get.assert_called_once_with(support_user.id, mock_db)


# ── get_by_id ─────────────────────────────────────────────────────────────────


class TestGetById:
    def test_returns_event_when_found(self, mock_db):
        event = EventFactory()
        with patch.object(Event, "get_by_id", return_value=event):
            result = EventService.get_by_id(event.id, mock_db)

        assert result == event

    def test_returns_none_when_not_found(self, mock_db):
        with patch.object(Event, "get_by_id", return_value=None):
            result = EventService.get_by_id(uuid.uuid4(), mock_db)

        assert result is None

    def test_passes_correct_id_to_model(self, mock_db):
        event_id = uuid.uuid4()

        with patch.object(Event, "get_by_id", return_value=None) as mock_get:
            EventService.get_by_id(event_id, mock_db)

        mock_get.assert_called_once_with(event_id, mock_db)


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def _make_data(self, **kwargs) -> EventCreateInput:
        event = EventFactory()
        data = EventCreateInput(
            contract_id=event.contract_id,
            customer_id=event.customer_id,
            support_id=None,
            start_date=event.start_date,
            end_date=event.end_date,
            location=event.location,
            attendees=event.attendees,
            notes=None,
        )
        if kwargs:
            data = data.model_copy(update=kwargs)
        return data

    def test_create_returns_event(self, mock_db):
        data = self._make_data()
        created_event = EventFactory()

        with patch.object(Event, "create", return_value=created_event):
            result = EventService.create(data, mock_db)

        assert result == created_event

    def test_create_passes_correct_args_to_model(self, mock_db):
        support_id = uuid.uuid4()
        data = self._make_data(support_id=support_id, notes="VIP event")
        created_event = EventFactory()

        with patch.object(Event, "create", return_value=created_event) as mock_create:
            EventService.create(data, mock_db)

        mock_create.assert_called_once_with(
            contract_id=data.contract_id,
            customer_id=data.customer_id,
            support_id=data.support_id,
            start_date=data.start_date,
            end_date=data.end_date,
            location=data.location,
            attendees=data.attendees,
            notes=data.notes,
            db=mock_db,
        )

    def test_create_without_optional_fields(self, mock_db):
        """support_id and notes are optional — service must forward None values."""
        data = self._make_data(support_id=None, notes=None)
        created_event = EventFactory()

        with patch.object(Event, "create", return_value=created_event) as mock_create:
            EventService.create(data, mock_db)

        _, kwargs = mock_create.call_args
        assert kwargs["support_id"] is None
        assert kwargs["notes"] is None

    def test_create_any_role_can_call_service(self, mock_db):
        """The service has no role check — that is the controller's responsibility."""
        data = self._make_data()
        created_event = EventFactory()

        with patch.object(Event, "create", return_value=created_event):
            result = EventService.create(data, mock_db)

        assert result == created_event


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_update_returns_updated_event(self, mock_db):
        target = EventFactory()
        data = EventUpdateInput(location="Lyon")
        updated_event = EventFactory(location="Lyon")

        with patch.object(Event, "update", return_value=updated_event):
            result = EventService.update(target, data, mock_db)

        assert result == updated_event

    def test_update_calls_update_on_target(self, mock_db):
        target = EventFactory()
        data = EventUpdateInput(attendees=100)
        target.update = MagicMock(return_value=target)

        EventService.update(target, data, mock_db)

        target.update.assert_called_once_with(data, mock_db)

    def test_update_any_role_can_call_service(self, mock_db):
        """The service itself has no role check — that is the controller's responsibility."""
        target = EventFactory()
        data = EventUpdateInput(notes="Updated note")
        target.update = MagicMock(return_value=target)

        EventService.update(target, data, mock_db)

        target.update.assert_called_once()


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_delete_calls_delete_on_target(self, mock_db):
        target = EventFactory()
        target.delete = MagicMock(return_value=None)

        EventService.delete(target, mock_db)

        target.delete.assert_called_once_with(mock_db)

    def test_delete_returns_none(self, mock_db):
        target = EventFactory()

        with patch.object(Event, "delete", return_value=None):
            result = EventService.delete(target, mock_db)

        assert result is None
