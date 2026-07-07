import uuid

import pytest

from crm_epic_events.errors import CompanyAlreadyExistsError
from crm_epic_events.services.company.schemas import CompanyCreateInput, CompanyUpdateInput
from crm_epic_events.services.company.service import CompanyService
from crm_epic_events.utils.constants import Roles
from tests.factories import VAT_NUMBER, CompanyDBFactory, CustomerDBFactory, UserDBFactory


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_returns_all_companies(self, db_session):
        CompanyDBFactory.create_batch(3)
        result = CompanyService.get_all(db_session)
        assert len(result) == 3

    def test_returns_empty_list(self, db_session):
        result = CompanyService.get_all(db_session)
        assert result == []


# ── get_by_customers_salesperson ──────────────────────────────────────────────


class TestGetByCustomersSalesperson:
    def test_returns_companies_linked_to_salesperson(self, db_session):
        salesperson = UserDBFactory(role=Roles.SALES)
        customer = CustomerDBFactory(salesperson=salesperson, salesperson_id=salesperson.id)
        result = CompanyService.get_by_customers_salesperson(salesperson.id, db_session)
        assert len(result) == 1
        assert result[0].vat_number == customer.company.vat_number

    def test_returns_empty_list_when_no_match(self, db_session):
        result = CompanyService.get_by_customers_salesperson(uuid.uuid4(), db_session)
        assert result == []

    def test_does_not_return_companies_of_other_salesperson(self, db_session):
        salesperson = UserDBFactory(role=Roles.SALES)
        CustomerDBFactory()  # autre salesperson
        result = CompanyService.get_by_customers_salesperson(salesperson.id, db_session)
        assert result == []


# ── get_by_vat ────────────────────────────────────────────────────────────────


class TestGetByVat:
    def test_returns_company_when_found(self, db_session):
        company = CompanyDBFactory()
        result = CompanyService.get_by_vat(company.vat_number, db_session)
        assert result is not None
        assert result.vat_number == company.vat_number

    def test_returns_none_when_not_found(self, db_session):
        result = CompanyService.get_by_vat("UNKNOWN_VAT", db_session)
        assert result is None


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def test_creates_and_returns_company(self, db_session):
        data = CompanyCreateInput(vat_number=VAT_NUMBER, name="Acme Corp")
        result = CompanyService.create(data, db_session)
        assert result.vat_number == VAT_NUMBER
        assert result.name == "Acme Corp"

    def test_company_is_persisted(self, db_session):
        data = CompanyCreateInput(vat_number=VAT_NUMBER, name="Acme Corp")
        CompanyService.create(data, db_session)
        result = CompanyService.get_by_vat(VAT_NUMBER, db_session)
        assert result is not None

    def test_raises_if_vat_already_exists(self, db_session):
        CompanyDBFactory(vat_number=VAT_NUMBER)
        data = CompanyCreateInput(vat_number=VAT_NUMBER, name="Duplicate Corp")
        with pytest.raises(CompanyAlreadyExistsError):
            CompanyService.create(data, db_session)


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_updates_name(self, db_session):
        company = CompanyDBFactory(name="Old Name")
        data = CompanyUpdateInput(name="New Name")
        updated = CompanyService.update(company, data, db_session)
        assert updated.name == "New Name"

    def test_partial_update_does_not_affect_vat(self, db_session):
        company = CompanyDBFactory(vat_number=VAT_NUMBER)
        data = CompanyUpdateInput(name="New Name")
        updated = CompanyService.update(company, data, db_session)
        assert updated.vat_number == VAT_NUMBER


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_deletes_company(self, db_session):
        company = CompanyDBFactory()
        vat = company.vat_number
        CompanyService.delete(company, db_session)
        assert CompanyService.get_by_vat(vat, db_session) is None

    def test_delete_returns_none(self, db_session):
        company = CompanyDBFactory()
        result = CompanyService.delete(company, db_session)
        assert result is None
