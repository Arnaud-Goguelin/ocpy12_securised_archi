import uuid

import pytest

from crm_epic_events.errors import CompanyAlreadyExistsError
from crm_epic_events.services.company.schemas import CompanyCreateInput, CompanyUpdateInput
from crm_epic_events.services.company.service import CompanyService
from tests.factories import VAT_NUMBER, CompanyDBFactory, CustomerDBFactory


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
    def test_returns_companies_linked_to_salesperson(self, db_session, salesperson, customer):
        customer.salesperson = salesperson
        result = CompanyService.get_by_customers_salesperson(salesperson.id, db_session)
        assert len(result) == 1
        assert result[0].vat_number == customer.company.vat_number

    def test_returns_empty_list_when_no_match(self, db_session):
        result = CompanyService.get_by_customers_salesperson(uuid.uuid4(), db_session)
        assert result == []

    def test_does_not_return_companies_of_other_salesperson(self, db_session, salesperson):
        CustomerDBFactory()  # create another customer not linked to salesperson to expect empty list as result
        result = CompanyService.get_by_customers_salesperson(salesperson.id, db_session)
        assert result == []


# ── get_by_vat ────────────────────────────────────────────────────────────────


class TestGetByVat:
    def test_returns_company_when_found(self, db_session, company):
        result = CompanyService.get_by_vat(company.vat_number, db_session)
        assert result is not None
        assert result.vat_number == company.vat_number

    def test_returns_none_when_not_found(self, db_session):
        result = CompanyService.get_by_vat("UNKNOWN_VAT", db_session)
        assert result is None


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def test_creates_and_returns_company(self, db_session, company_create_data):
        result = CompanyService.create(company_create_data, db_session)
        assert result.vat_number == VAT_NUMBER
        assert result.name == company_create_data.name

    def test_company_is_persisted(self, db_session, company_create_data):
        CompanyService.create(company_create_data, db_session)
        result = CompanyService.get_by_vat(VAT_NUMBER, db_session)
        assert result is not None

    def test_raises_if_vat_already_exists(self, db_session, company):
        # create another set of data to try to create a company with the same VAT number but another name
        company_create_data = CompanyCreateInput(vat_number=company.vat_number, name="other name")
        with pytest.raises(CompanyAlreadyExistsError):
            CompanyService.create(company_create_data, db_session)


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_updates_name_without_affect_vat_number(self, db_session, company):
        data = CompanyUpdateInput(name="New Name")
        updated = CompanyService.update(company, data, db_session)
        assert updated.name == "New Name"
        assert updated.vat_number == company.vat_number


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_deletes_company(self, db_session, company):
        vat = company.vat_number
        CompanyService.delete(company, db_session)
        assert CompanyService.get_by_vat(vat, db_session) is None

    def test_delete_returns_none(self, db_session, company):
        result = CompanyService.delete(company, db_session)
        assert result is None
