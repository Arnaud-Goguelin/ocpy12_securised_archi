from unittest.mock import MagicMock, patch

import pytest

from crm_epic_events.controllers.contract import ContractController
from crm_epic_events.errors import UserIsNotOwnerError, UserNotAllowedError
from crm_epic_events.services.contract.service import ContractService
from crm_epic_events.services.customer.service import CustomerService
from crm_epic_events.utils.constants import NavSignal, Roles, StandardInputs
from tests.factories import ContractFactory, CustomerFactory, UserFactory


# ── handle_list ───────────────────────────────────────────────────────────────


class TestHandleList:
    def test_any_role_can_list(self, mock_db):
        for role in Roles:
            user = UserFactory(role=role)
            ctrl = ContractController(mock_db, user)
            with patch.object(ContractService, "get_all", return_value=[]):
                signal = ctrl.handle_list()
            assert signal == NavSignal.STAY


# ── handle_list_unsigned ──────────────────────────────────────────────────────


class TestHandleListUnsigned:
    def test_manager_can_list_unsigned(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        with patch.object(ContractService, "get_unsigned", return_value=[]):
            signal = ctrl.handle_list_unsigned()
        assert signal == NavSignal.STAY

    def test_sales_can_list_unsigned(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = ContractController(mock_db, user)
        with patch.object(ContractService, "get_unsigned", return_value=[]):
            signal = ctrl.handle_list_unsigned()
        assert signal == NavSignal.STAY


# ── handle_create ─────────────────────────────────────────────────────────────


class TestHandleCreate:
    def test_manager_can_create(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        customers = CustomerFactory.build_batch(2)
        contract = ContractFactory()
        ctrl.view.prompt_create = MagicMock(
            return_value=(
                "1",
                {
                    "total_amount": "1000",
                    "remaining_amount": "500",
                    "status": False,
                },
            )
        )

        with (
            patch.object(CustomerService, "get_all", return_value=customers),
            patch.object(ContractService, "create", return_value=contract),
        ):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_sales_cannot_create(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = ContractController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_create()

    def test_support_cannot_create(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = ContractController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_create()

    def test_no_customers_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)

        with patch.object(CustomerService, "get_all", return_value=[]):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_invalid_customer_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        customers = CustomerFactory.build_batch(2)
        ctrl.view.prompt_create = MagicMock(return_value=("invalid", {}))

        with patch.object(CustomerService, "get_all", return_value=customers):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY


# ── handle_update ─────────────────────────────────────────────────────────────


class TestHandleUpdate:
    def test_manager_can_update_any_contract(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        contracts = ContractFactory.build_batch(2)
        ctrl.view.prompt_select_contract = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={"status": True})

        with (
            patch.object(ContractService, "get_all", return_value=contracts),
            patch.object(ContractService, "update", return_value=contracts[0]),
        ):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_sales_can_update_own_contract(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        contract = ContractFactory(salesperson_id=user.id)
        contract.salesperson = user
        ctrl = ContractController(mock_db, user)
        ctrl.view.prompt_select_contract = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={"status": True})

        with (
            patch.object(ContractService, "get_all_by_salesperson", return_value=[contract]),
            patch.object(ContractService, "update", return_value=contract),
        ):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_sales_cannot_update_other_salesperson_contract(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        other_user = UserFactory(role=Roles.SALES)
        contract = ContractFactory(salesperson_id=other_user.id)
        contract.salesperson = other_user
        ctrl = ContractController(mock_db, user)
        ctrl.view.prompt_select_contract = MagicMock(return_value="1")

        with (
            patch.object(ContractService, "get_all_by_salesperson", return_value=[contract]),
            pytest.raises(UserIsNotOwnerError),
        ):
            ctrl.handle_update()

    def test_support_cannot_update(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = ContractController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_update()

    def test_cancelled_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        ctrl.view.prompt_select_contract = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(ContractService, "get_all", return_value=[]):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        contracts = ContractFactory.build_batch(2)
        ctrl.view.prompt_select_contract = MagicMock(return_value="invalid")

        with patch.object(ContractService, "get_all", return_value=contracts):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_nothing_to_update_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        contracts = ContractFactory.build_batch(2)
        ctrl.view.prompt_select_contract = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={})

        with patch.object(ContractService, "get_all", return_value=contracts):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY


# ── handle_delete ─────────────────────────────────────────────────────────────


class TestHandleDelete:
    def test_manager_can_delete(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        contracts = ContractFactory.build_batch(2)
        ctrl.view.prompt_select_contract = MagicMock(return_value="1")

        with (
            patch.object(ContractService, "get_all", return_value=contracts),
            patch.object(ContractService, "delete") as mock_delete,
        ):
            signal = ctrl.handle_delete()

        mock_delete.assert_called_once_with(contracts[0], mock_db)
        assert signal == NavSignal.STAY

    def test_sales_cannot_delete(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = ContractController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_delete()

    def test_support_cannot_delete(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = ContractController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_delete()

    def test_cancelled_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        ctrl.view.prompt_select_contract = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(ContractService, "get_all", return_value=[]):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = ContractController(mock_db, user)
        contracts = ContractFactory.build_batch(2)
        ctrl.view.prompt_select_contract = MagicMock(return_value="invalid")

        with patch.object(ContractService, "get_all", return_value=contracts):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY
