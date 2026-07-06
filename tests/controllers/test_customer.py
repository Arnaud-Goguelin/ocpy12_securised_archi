from unittest.mock import patch

import pytest

from crm_epic_events.controllers.company import CompanyController
from crm_epic_events.errors import CompanyAlreadyExistsError, UserNotAllowedError
from crm_epic_events.services.company.service import CompanyService
from crm_epic_events.utils.constants import NavSignal, Roles
from tests.factories import CompanyFactory, UserFactory


class TestCompanyControllerHandleList:
    def test_list_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)

        with patch.object(CompanyService, "get_all", return_value=[]):
            signal = ctrl.handle_list()

        assert signal == NavSignal.STAY

    def test_list_calls_get_all(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)

        with patch.object(CompanyService, "get_all", return_value=[]) as mock_get:
            ctrl.handle_list()

        mock_get.assert_called_once_with(mock_db)


class TestCompanyControllerHandleCreate:
    def test_manager_can_create(self, mock_db, capsys):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        company = CompanyFactory()

        with (
            patch.object(
                ctrl.view, "prompt_create", return_value={"vat_number": company.vat_number, "name": company.name}
            ),
            patch.object(CompanyService, "create", return_value=company),
        ):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_sales_can_create(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = CompanyController(mock_db, user)
        company = CompanyFactory()

        with (
            patch.object(
                ctrl.view, "prompt_create", return_value={"vat_number": company.vat_number, "name": company.name}
            ),
            patch.object(CompanyService, "create", return_value=company),
        ):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY

    def test_support_cannot_create(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = CompanyController(mock_db, user)

        with pytest.raises(UserNotAllowedError):
            ctrl.handle_create()

    def test_duplicate_vat_shows_error(self, mock_db, capsys):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        company = CompanyFactory()

        with (
            patch.object(
                ctrl.view, "prompt_create", return_value={"vat_number": company.vat_number, "name": company.name}
            ),
            patch.object(CompanyService, "create", side_effect=CompanyAlreadyExistsError()),
        ):
            signal = ctrl.handle_create()

        assert signal == NavSignal.STAY
        captured = capsys.readouterr()
        assert "already exists" in captured.out


class TestCompanyControllerHandleDelete:
    def test_manager_can_delete(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        companies = CompanyFactory.build_batch(2)

        with (
            patch.object(CompanyService, "get_all", return_value=companies),
            patch.object(ctrl.view, "prompt_select_company", return_value="1"),
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

    def test_invalid_selection_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)
        companies = CompanyFactory.build_batch(2)

        with (
            patch.object(CompanyService, "get_all", return_value=companies),
            patch.object(ctrl.view, "prompt_select_company", return_value="invalid"),
        ):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY

    def test_cancelled_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = CompanyController(mock_db, user)

        with (
            patch.object(CompanyService, "get_all", return_value=[]),
            patch.object(ctrl.view, "prompt_select_company", return_value="Q"),
        ):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY
