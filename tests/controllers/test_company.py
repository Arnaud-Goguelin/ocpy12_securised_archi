from unittest.mock import MagicMock, patch

import pytest

from crm_epic_events.controllers.company import CompanyController
from crm_epic_events.errors import CompanyAlreadyExistsError, UserNotAllowedError
from crm_epic_events.services.company.service import CompanyService
from crm_epic_events.utils.constants import NavSignal, Roles, StandardInputs
from tests.factories import CompanyFactory, UserFactory


# ── handle_list ───────────────────────────────────────────────────────────────


class TestHandleList:
    def test_any_role_can_list(self, mock_db):
        for role in Roles:
            user = UserFactory(role=role)
            ctrl = CompanyController(mock_db, user)
            with patch.object(CompanyService, "get_all", return_value=[]):
                signal = ctrl.handle_list()
            assert signal == NavSignal.STAY

    def test_calls_get_all(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        with patch.object(CompanyService, "get_all", return_value=[]) as mock_get:
            ctrl.handle_list()
        mock_get.assert_called_once_with(mock_db)


# ── handle_create ─────────────────────────────────────────────────────────────


class TestHandleCreate:
    def test_manager_can_create(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        company = CompanyFactory()
        ctrl.view.prompt_create = MagicMock(return_value={"vat_number": company.vat_number, "name": company.name})

        with patch.object(CompanyService, "create", return_value=company):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_sales_can_create(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = CompanyController(mock_db, user)
        company = CompanyFactory()
        ctrl.view.prompt_create = MagicMock(return_value={"vat_number": company.vat_number, "name": company.name})

        with patch.object(CompanyService, "create", return_value=company):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_support_cannot_create(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = CompanyController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_create()

    def test_duplicate_vat_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        company = CompanyFactory()
        ctrl.view.prompt_create = MagicMock(return_value={"vat_number": company.vat_number, "name": company.name})

        with patch.object(CompanyService, "create", side_effect=CompanyAlreadyExistsError()):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_calls_service_create_with_correct_data(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        company = CompanyFactory()
        ctrl.view.prompt_create = MagicMock(return_value={"vat_number": company.vat_number, "name": company.name})

        with patch.object(CompanyService, "create", return_value=company) as mock_create:
            ctrl.handle_create()

        mock_create.assert_called_once()


# ── handle_update ─────────────────────────────────────────────────────────────


class TestHandleUpdate:
    def test_manager_can_update(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        companies = CompanyFactory.build_batch(2)
        ctrl.view.prompt_select_company = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={"name": "New Name"})

        with (
            patch.object(CompanyService, "get_all", return_value=companies),
            patch.object(CompanyService, "update", return_value=companies[0]),
        ):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_sales_can_update_own_company(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = CompanyController(mock_db, user)
        companies = CompanyFactory.build_batch(2)
        ctrl.view.prompt_select_company = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={"name": "New Name"})

        with (
            patch.object(CompanyService, "get_by_customers_salesperson", return_value=companies),
            patch.object(CompanyService, "update", return_value=companies[0]),
        ):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_support_cannot_update(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = CompanyController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_update()

    def test_cancelled_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        ctrl.view.prompt_select_company = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(CompanyService, "get_all", return_value=[]):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        companies = CompanyFactory.build_batch(2)
        ctrl.view.prompt_select_company = MagicMock(return_value="invalid")

        with patch.object(CompanyService, "get_all", return_value=companies):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY

    def test_nothing_to_update_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        companies = CompanyFactory.build_batch(2)
        ctrl.view.prompt_select_company = MagicMock(return_value="1")
        ctrl.view.prompt_update = MagicMock(return_value={})

        with patch.object(CompanyService, "get_all", return_value=companies):
            signal = ctrl.handle_update()

        assert signal == NavSignal.STAY


# ── handle_delete ─────────────────────────────────────────────────────────────


class TestHandleDelete:
    def test_manager_can_delete(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        companies = CompanyFactory.build_batch(2)
        ctrl.view.prompt_select_company = MagicMock(return_value="1")

        with (
            patch.object(CompanyService, "get_all", return_value=companies),
            patch.object(CompanyService, "delete") as mock_delete,
        ):
            signal = ctrl.handle_delete()

        mock_delete.assert_called_once_with(companies[0], mock_db)
        assert signal == NavSignal.STAY

    def test_sales_cannot_delete(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = CompanyController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_delete()

    def test_support_cannot_delete(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = CompanyController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_delete()

    def test_cancelled_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        ctrl.view.prompt_select_company = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(CompanyService, "get_all", return_value=[]):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        companies = CompanyFactory.build_batch(2)
        ctrl.view.prompt_select_company = MagicMock(return_value="invalid")

        with patch.object(CompanyService, "get_all", return_value=companies):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY
