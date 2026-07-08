from crm_epic_events.services.company.service import CompanyService
from crm_epic_events.services.customer.schemas import CustomerUpdateInput
from crm_epic_events.services.customer.service import CustomerService
from tests.factories import (
    VAT_NUMBER,
    CompanyDBFactory,
    CustomerDBFactory,
)


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_returns_all_customers(self, db_session):
        CustomerDBFactory.create_batch(3)
        result = CustomerService.get_all(db_session)
        assert len(result) == 3

    def test_returns_empty_list(self, db_session):
        result = CustomerService.get_all(db_session)
        assert result == []


# ── get_all_by_salesperson ────────────────────────────────────────────────────


class TestGetAllBySalesperson:
    def test_returns_customers_for_salesperson(self, db_session, salesperson, customer):
        customer.salesperson = salesperson
        CustomerDBFactory()  # create another customer not linked to salesperson to expect a list with only 1 object
        result = CustomerService.get_all_by_salesperson(salesperson, db_session)
        assert len(result) == 1
        assert result[0].salesperson_id == salesperson.id

    def test_returns_empty_list_when_no_customers(self, db_session, salesperson):
        result = CustomerService.get_all_by_salesperson(salesperson, db_session)
        assert result == []


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def test_creates_and_returns_customer(self, db_session, salesperson, customer_create_data):
        customer = CustomerService.create(salesperson, customer_create_data, db_session)
        assert customer.first_name == customer_create_data.first_name
        assert customer.last_name == customer_create_data.last_name
        assert customer.salesperson_id == salesperson.id

    def test_customer_is_persisted(self, db_session, salesperson, customer_create_data):
        customer = CustomerService.create(salesperson, customer_create_data, db_session)
        result = CustomerService.get_all(db_session)
        assert any(c.id == customer.id for c in result)

    def test_auto_creates_company_when_not_found(self, db_session, salesperson, customer_create_data):
        assert CompanyService.get_by_vat(VAT_NUMBER, db_session) is None
        CustomerService.create(salesperson, customer_create_data, db_session)
        assert CompanyService.get_by_vat(VAT_NUMBER, db_session) is not None

    def test_uses_existing_company_when_found(self, db_session, salesperson, customer_create_data):
        CompanyDBFactory(vat_number=VAT_NUMBER)
        CustomerService.create(salesperson, customer_create_data, db_session)
        companies = CompanyService.get_all(db_session)
        assert len([c for c in companies if c.vat_number == VAT_NUMBER]) == 1

    def test_salesperson_is_inherited_from_current_user(self, db_session, salesperson, customer_create_data):
        customer = CustomerService.create(salesperson, customer_create_data, db_session)
        assert customer.salesperson_id == salesperson.id


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_updates_first_name(self, db_session, customer):
        data = CustomerUpdateInput(first_name="New first name")
        updated = CustomerService.update(customer, data, db_session)
        assert updated.first_name == "New first name"

    def test_partial_update_does_not_affect_other_fields(self, db_session, customer):
        data = CustomerUpdateInput(first_name="New first name")
        updated = CustomerService.update(customer, data, db_session)
        assert updated.last_name == customer.last_name


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_deletes_customer(self, db_session, customer):
        customer_id = customer.id
        CustomerService.delete(customer, db_session)
        result = CustomerService.get_all(db_session)
        assert not any(c.id == customer_id for c in result)

    def test_delete_returns_none(self, db_session, customer):
        result = CustomerService.delete(customer, db_session)
        assert result is None

    def test_deletes_orphan_company(self, db_session, customer):
        company_vat = customer.company_vat
        CustomerService.delete(customer, db_session)
        assert CompanyService.get_by_vat(company_vat, db_session) is None

    def test_keeps_company_when_other_customers_exist(self, db_session, company):
        customer1 = CustomerDBFactory(company=company, company_vat=company.vat_number)
        customer2 = CustomerDBFactory(company=company, company_vat=company.vat_number)
        CustomerService.delete(customer1, db_session)
        assert CompanyService.get_by_vat(company.vat_number, db_session) is not None
        remaining = CustomerService.get_all(db_session)
        assert any(c.id == customer2.id for c in remaining)
