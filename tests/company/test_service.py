# tests/services/company/test_service.py
from unittest.mock import MagicMock, patch

import pytest

from crm_epic_events.errors import UserNotAllowedError
from crm_epic_events.models.company import Company
from crm_epic_events.services.company.schemas import CompanyCreateInput, CompanyUpdateInput
from crm_epic_events.services.company.service import CompanyService
from crm_epic_events.utils import Roles
from tests.factories import CompanyFactory, UserFactory


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_get_all_returns_companies(self, mock_db):
        companies = CompanyFactory.build_batch(3)
        with patch.object(Company, "get_all", return_value=companies):
            result = CompanyService.get_all(mock_db)

        assert result == companies

    def test_get_all_returns_empty_list(self, mock_db):
        with patch.object(Company, "get_all", return_value=[]):
            result = CompanyService.get_all(mock_db)

        assert result == []


# ── get_by_customers_salesperson ──────────────────────────────────────────────


class TestGetByCustomersSalesperson:
    def test_returns_companies_linked_to_salesperson(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        companies = CompanyFactory.build_batch(2)

        with patch.object(Company, "get_by_customers_salesperson", return_value=companies):
            result = CompanyService.get_by_customers_salesperson(sales_user.id, mock_db)

        assert result == companies

    def test_returns_empty_list_when_no_match(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)

        with patch.object(Company, "get_by_customers_salesperson", return_value=[]):
            result = CompanyService.get_by_customers_salesperson(sales_user.id, mock_db)

        assert result == []


# ── get_by_vat ────────────────────────────────────────────────────────────────


class TestGetByVat:
    def test_returns_company_when_found(self, mock_db):
        company = CompanyFactory()

        with patch.object(Company, "get_by_vat", return_value=company):
            result = CompanyService.get_by_vat(company.vat_number, mock_db)

        assert result == company

    def test_returns_none_when_not_found(self, mock_db):
        with patch.object(Company, "get_by_vat", return_value=None):
            result = CompanyService.get_by_vat("UNKNOWN_VAT", mock_db)

        assert result is None


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def test_manager_can_create_company(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        data = CompanyCreateInput(vat_number="FR0123456789", name="company test")
        created_company = CompanyFactory()

        with (
            patch.object(Company, "get_by_vat", return_value=None),
            patch.object(Company, "create", return_value=created_company),
        ):
            result = CompanyService.create(manager, data, mock_db)

        assert result == created_company

    def test_sales_can_create_company(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        data = CompanyCreateInput(vat_number="FR0123456789", name="company test")
        created_company = CompanyFactory()

        with (
            patch.object(Company, "get_by_vat", return_value=None),
            patch.object(Company, "create", return_value=created_company),
        ):
            result = CompanyService.create(sales_user, data, mock_db)

        assert result == created_company

    def test_support_cannot_create_company(self, mock_db):
        support_user = UserFactory(role=Roles.SUPPORT)
        data = CompanyCreateInput(vat_number="FR0123456789", name="company test")

        with pytest.raises(UserNotAllowedError):
            CompanyService.create(support_user, data, mock_db)

    def test_create_raises_if_vat_already_exists(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        existing_company = CompanyFactory(vat_number="FR0123456789")
        data = CompanyCreateInput(vat_number="FR0123456789", name="company test")

        with (
            patch.object(Company, "get_by_vat", return_value=existing_company),
            pytest.raises(ValueError, match="already exists"),
        ):
            CompanyService.create(manager, data, mock_db)

    def test_create_calls_model_with_correct_args(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        data = CompanyCreateInput(vat_number="FR0123456789", name="company test")
        created_company = CompanyFactory()

        with (
            patch.object(Company, "get_by_vat", return_value=None),
            patch.object(Company, "create", return_value=created_company) as mock_create,
        ):
            CompanyService.create(manager, data, mock_db)

        mock_create.assert_called_once_with("FR0123456789", "company test", mock_db)


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_manager_can_update_company(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = CompanyFactory()
        data = CompanyUpdateInput(name="New Name")
        updated_company = CompanyFactory(vat_number=target.vat_number, name="New Name")

        with patch.object(Company, "update", return_value=updated_company):
            result = CompanyService.update(manager, target, data, mock_db)

        assert result == updated_company

    def test_sales_can_update_company(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        target = CompanyFactory()
        data = CompanyUpdateInput(name="New Name")
        updated_company = CompanyFactory(vat_number=target.vat_number, name="New Name")

        with patch.object(Company, "update", return_value=updated_company):
            result = CompanyService.update(sales_user, target, data, mock_db)

        assert result == updated_company

    def test_support_cannot_update_company(self, mock_db):
        support_user = UserFactory(role=Roles.SUPPORT)
        target = CompanyFactory()
        data = CompanyUpdateInput(name="New Name")

        with pytest.raises(UserNotAllowedError):
            CompanyService.update(support_user, target, data, mock_db)

    def test_update_calls_update_on_target(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = CompanyFactory()
        data = CompanyUpdateInput(name="New Name")

        target.update = MagicMock(return_value=target)

        CompanyService.update(manager, target, data, mock_db)

        target.update.assert_called_once_with(data, mock_db)


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_manager_can_delete_company(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = CompanyFactory()

        target.delete = MagicMock(return_value=None)

        CompanyService.delete(manager, target, mock_db)

        target.delete.assert_called_once_with(mock_db)

    def test_sales_cannot_delete_company(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        target = CompanyFactory()

        with pytest.raises(UserNotAllowedError):
            CompanyService.delete(sales_user, target, mock_db)

    def test_support_cannot_delete_company(self, mock_db):
        support_user = UserFactory(role=Roles.SUPPORT)
        target = CompanyFactory()

        with pytest.raises(UserNotAllowedError):
            CompanyService.delete(support_user, target, mock_db)

    def test_delete_returns_none(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = CompanyFactory()

        with patch.object(Company, "delete", return_value=None):
            result = CompanyService.delete(manager, target, mock_db)

        assert result is None
