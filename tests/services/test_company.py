from unittest.mock import MagicMock, patch

import pytest

from crm_epic_events.errors import CompanyAlreadyExistsError
from crm_epic_events.models.company import Company
from crm_epic_events.services.company.schemas import CompanyCreateInput, CompanyUpdateInput
from crm_epic_events.services.company.service import CompanyService
from tests.factories import VAT_NUMBER, CompanyFactory


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
        companies = CompanyFactory.build_batch(2)
        user_id = companies[0].vat_number  # any uuid-like value

        with patch.object(Company, "get_by_customers_salesperson", return_value=companies):
            result = CompanyService.get_by_customers_salesperson(user_id, mock_db)

        assert result == companies

    def test_returns_empty_list_when_no_match(self, mock_db):
        with patch.object(Company, "get_by_customers_salesperson", return_value=[]):
            result = CompanyService.get_by_customers_salesperson("any-id", mock_db)

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
    def test_create_returns_company(self, mock_db):
        data = CompanyCreateInput(vat_number=VAT_NUMBER, name="Acme Corp")
        created_company = CompanyFactory()

        with (
            patch.object(Company, "get_by_vat", return_value=None),
            patch.object(Company, "create", return_value=created_company),
        ):
            result = CompanyService.create(data, mock_db)

        assert result == created_company

    def test_create_raises_if_vat_already_exists(self, mock_db):
        existing_company = CompanyFactory(vat_number=VAT_NUMBER)
        data = CompanyCreateInput(vat_number=VAT_NUMBER, name="Acme Corp")

        with (
            patch.object(Company, "get_by_vat", return_value=existing_company),
            pytest.raises(CompanyAlreadyExistsError),
        ):
            CompanyService.create(data, mock_db)

    def test_create_calls_model_with_correct_args(self, mock_db):
        data = CompanyCreateInput(vat_number=VAT_NUMBER, name="Acme Corp")
        created_company = CompanyFactory()

        with (
            patch.object(Company, "get_by_vat", return_value=None),
            patch.object(Company, "create", return_value=created_company) as mock_create,
        ):
            CompanyService.create(data, mock_db)

        mock_create.assert_called_once_with(VAT_NUMBER, "Acme Corp", mock_db)


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_update_returns_updated_company(self, mock_db):
        target = CompanyFactory()
        data = CompanyUpdateInput(name="New Name")
        updated_company = CompanyFactory(vat_number=target.vat_number, name="New Name")

        with patch.object(Company, "update", return_value=updated_company):
            result = CompanyService.update(target, data, mock_db)

        assert result == updated_company

    def test_update_calls_update_on_target(self, mock_db):
        target = CompanyFactory()
        data = CompanyUpdateInput(name="New Name")
        target.update = MagicMock(return_value=target)

        CompanyService.update(target, data, mock_db)

        target.update.assert_called_once_with(data, mock_db)

    def test_update_any_role_can_call_service(self, mock_db):
        """The service has no role check — that is the controller's responsibility."""
        target = CompanyFactory()
        data = CompanyUpdateInput(name="New Name")
        target.update = MagicMock(return_value=target)

        # Should not raise regardless of caller
        CompanyService.update(target, data, mock_db)

        target.update.assert_called_once()


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_delete_calls_delete_on_target(self, mock_db):
        target = CompanyFactory()
        target.delete = MagicMock(return_value=None)

        CompanyService.delete(target, mock_db)

        target.delete.assert_called_once_with(mock_db)

    def test_delete_returns_none(self, mock_db):
        target = CompanyFactory()
        target.delete = MagicMock(return_value=None)

        result = CompanyService.delete(target, mock_db)

        assert result is None

    def test_delete_any_role_can_call_service(self, mock_db):
        """The service has no role check — that is the controller's responsibility."""
        target = CompanyFactory()
        target.delete = MagicMock(return_value=None)

        # Should not raise regardless of caller
        CompanyService.delete(target, mock_db)

        target.delete.assert_called_once()
