from unittest.mock import MagicMock, patch

import pytest

from crm_epic_events.controllers.event import EventController
from crm_epic_events.errors import (
    ContractNotFoundError,
    ContractNotSignedError,
    UserIsNotOwnerError,
    UserNotAllowedError,
)
from crm_epic_events.services.contract.service import ContractService
from crm_epic_events.services.event.service import EventService
from crm_epic_events.utils.constants import NavSignal, Roles, StandardInputs
from tests.factories import ContractFactory, EventFactory, UserFactory


# ── handle_list ───────────────────────────────────────────────────────────────


class TestHandleList:
    def test_any_role_can_list(self, mock_db):
        for role in Roles:
            user = UserFactory(role=role)
            ctrl = EventController(mock_db, user)
            with patch.object(EventService, "get_all", return_value=[]):
                signal = ctrl.handle_list()
            assert signal == NavSignal.STAY


# ── handle_list_without_support ───────────────────────────────────────────────


class TestHandleListWithoutSupport:
    def test_manager_can_list_without_support(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        with patch.object(EventService, "get_all_without_support", return_value=[]):
            signal = ctrl.handle_list_without_support()
        assert signal == NavSignal.STAY

    def test_sales_cannot_list_without_support(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_list_without_support()

    def test_support_cannot_list_without_support(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = EventController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_list_without_support()


# ── handle_create ─────────────────────────────────────────────────────────────


class TestHandleCreate:
    def _make_signed_contract(self, user):
        contract = ContractFactory(salesperson_id=user.id, status=True)
        contract.customer = MagicMock()
        contract.customer_id = contract.customer_id
        return contract

    def test_sales_can_create(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)
        contract = self._make_signed_contract(user)
        event = EventFactory()
        ctrl.view.prompt_create = MagicMock(
            return_value=(
                "1",
                {
                    "start_date": "2025-06-01 10:00",
                    "end_date": "2025-06-02 10:00",
                    "location": "Paris",
                    "attendees": "50",
                    "notes": None,
                },
            )
        )

        with (
            patch.object(ContractService, "get_all_by_salesperson", return_value=[contract]),
            patch.object(EventService, "create", return_value=event),
        ):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_manager_cannot_create(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_create()

    def test_support_cannot_create(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = EventController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_create()

    def test_no_signed_contracts_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)

        with patch.object(ContractService, "get_all_by_salesperson", return_value=[]):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_unsigned_contract_filtered_out(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)
        unsigned = ContractFactory(salesperson_id=user.id, status=False)

        with patch.object(ContractService, "get_all_by_salesperson", return_value=[unsigned]):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_contract_not_found_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)
        contract = self._make_signed_contract(user)
        ctrl.view.prompt_create = MagicMock(
            return_value=(
                "1",
                {
                    "start_date": "2025-06-01 10:00",
                    "end_date": "2025-06-02 10:00",
                    "location": "Paris",
                    "attendees": "50",
                    "notes": None,
                },
            )
        )

        with (
            patch.object(ContractService, "get_all_by_salesperson", return_value=[contract]),
            patch.object(EventService, "create", side_effect=ContractNotFoundError()),
        ):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_unsigned_contract_error_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)
        contract = self._make_signed_contract(user)
        ctrl.view.prompt_create = MagicMock(
            return_value=(
                "1",
                {
                    "start_date": "2025-06-01 10:00",
                    "end_date": "2025-06-02 10:00",
                    "location": "Paris",
                    "attendees": "50",
                    "notes": None,
                },
            )
        )

        with (
            patch.object(ContractService, "get_all_by_salesperson", return_value=[contract]),
            patch.object(EventService, "create", side_effect=ContractNotSignedError()),
        ):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)
        contract = self._make_signed_contract(user)
        ctrl.view.prompt_create = MagicMock(return_value=("invalid", {}))

        with patch.object(ContractService, "get_all_by_salesperson", return_value=[contract]):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY


# ── handle_update ─────────────────────────────────────────────────────────────


class TestHandleUpdate:
    def test_manager_can_update_any_event(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        events = EventFactory.build_batch(2)
        ctrl.view.prompt_select_event = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={"location": "Lyon"})

        with (
            patch.object(EventService, "get_all", return_value=events),
            patch.object(EventService, "update", return_value=events[0]),
        ):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_support_can_update_own_event(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        event = EventFactory(support_id=user.id)
        event.support = user
        ctrl = EventController(mock_db, user)
        ctrl.view.prompt_select_event = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={"location": "Lyon"})

        with (
            patch.object(EventService, "get_all_by_support", return_value=[event]),
            patch.object(EventService, "update", return_value=event),
        ):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_support_cannot_update_other_support_event(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        other_user = UserFactory(role=Roles.SUPPORT)
        event = EventFactory(support_id=other_user.id)
        event.support = other_user
        ctrl = EventController(mock_db, user)
        ctrl.view.prompt_select_event = MagicMock(return_value="1")

        with (
            patch.object(EventService, "get_all_by_support", return_value=[event]),
            pytest.raises(UserIsNotOwnerError),
        ):
            ctrl.handle_update()

    def test_sales_cannot_update(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_update()

    def test_cancelled_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        ctrl.view.prompt_select_event = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(EventService, "get_all", return_value=[]):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        events = EventFactory.build_batch(2)
        ctrl.view.prompt_select_event = MagicMock(return_value="invalid")

        with patch.object(EventService, "get_all", return_value=events):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_nothing_to_update_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        events = EventFactory.build_batch(2)
        ctrl.view.prompt_select_event = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={})

        with patch.object(EventService, "get_all", return_value=events):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY


# ── handle_delete ─────────────────────────────────────────────────────────────


class TestHandleDelete:
    def test_manager_can_delete(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        events = EventFactory.build_batch(2)
        ctrl.view.prompt_select_event = MagicMock(return_value="1")

        with (
            patch.object(EventService, "get_all", return_value=events),
            patch.object(EventService, "delete") as mock_delete,
        ):
            signal = ctrl.handle_delete()

        mock_delete.assert_called_once_with(events[0], mock_db)
        assert signal == NavSignal.STAY

    def test_sales_cannot_delete(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = EventController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_delete()

    def test_support_cannot_delete(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = EventController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_delete()

    def test_cancelled_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        ctrl.view.prompt_select_event = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(EventService, "get_all", return_value=[]):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = EventController(mock_db, user)
        events = EventFactory.build_batch(2)
        ctrl.view.prompt_select_event = MagicMock(return_value="invalid")

        with patch.object(EventService, "get_all", return_value=events):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY
