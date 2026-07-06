import uuid

from unittest.mock import MagicMock, patch

from crm_epic_events.models import Company
from crm_epic_events.models.customer import Customer
from crm_epic_events.services.company.service import CompanyService
from crm_epic_events.services.customer.schemas import CustomerCreateInput, CustomerUpdateInput
from crm_epic_events.services.customer.service import CustomerService
from crm_epic_events.utils import Roles
from tests.factories import VAT_NUMBER, CompanyFactory, CustomerFactory, UserFactory


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_get_all_returns_customers(self, mock_db):
        customers = CustomerFactory.build_batch(3)
        with patch.object(Customer, "get_all", return_value=customers):
            result = CustomerService.get_all(mock_db)

        assert result == customers

    def test_get_all_returns_empty_list(self, mock_db):
        with patch.object(Customer, "get_all", return_value=[]):
            result = CustomerService.get_all(mock_db)

        assert result == []


# ── get_all_by_salesperson ────────────────────────────────────────────────────


class TestGetAllBySalesperson:
    def test_returns_customers_for_salesperson(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        customers = CustomerFactory.build_batch(2, salesperson_id=sales_user.id)

        with patch.object(Customer, "get_all_by_salesperson", return_value=customers):
            result = CustomerService.get_all_by_salesperson(sales_user, mock_db)

        assert result == customers

    def test_returns_empty_list_when_no_customers(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)

        with patch.object(Customer, "get_all_by_salesperson", return_value=[]):
            result = CustomerService.get_all_by_salesperson(sales_user, mock_db)

        assert result == []

    def test_passes_salesperson_id_to_model(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)

        with patch.object(Customer, "get_all_by_salesperson", return_value=[]) as mock_get:
            CustomerService.get_all_by_salesperson(sales_user, mock_db)

        mock_get.assert_called_once_with(sales_user.id, mock_db)


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def _make_data(self, **kwargs) -> CustomerCreateInput:
        data = CustomerCreateInput(
            salesperson_id=uuid.uuid4(),
            company_vat=VAT_NUMBER,
            company_name="Acme Corp",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            phone="0600000000",
        )

        if kwargs:
            data = data.model_copy(update=kwargs)

        return data

    def test_create_uses_existing_company(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        existing_company = CompanyFactory(vat_number=VAT_NUMBER)
        data = self._make_data()
        created_customer = CustomerFactory()

        with (
            patch.object(CompanyService, "get_by_vat", return_value=existing_company) as mock_get_vat,
            patch.object(CompanyService, "create") as mock_company_create,
            patch.object(Customer, "create", return_value=created_customer),
        ):
            result = CustomerService.create(sales_user, data, mock_db)

        mock_get_vat.assert_called_once_with(data.company_vat, mock_db)
        mock_company_create.assert_not_called()
        assert result == created_customer

    def test_create_auto_creates_company_when_not_found(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        new_company = CompanyFactory(vat_number=VAT_NUMBER)
        data = self._make_data()
        created_customer = CustomerFactory()

        with (
            patch.object(CompanyService, "get_by_vat", return_value=None),
            patch.object(CompanyService, "create", return_value=new_company) as mock_company_create,
            patch.object(Customer, "create", return_value=created_customer),
        ):
            result = CustomerService.create(sales_user, data, mock_db)

        mock_company_create.assert_called_once_with(sales_user, data, mock_db)
        assert result == created_customer

    def test_create_passes_correct_args_to_customer_model(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        existing_company = CompanyFactory(vat_number=VAT_NUMBER)
        data = self._make_data()
        created_customer = CustomerFactory()

        with (
            patch.object(CompanyService, "get_by_vat", return_value=existing_company),
            patch.object(Customer, "create", return_value=created_customer) as mock_create,
        ):
            CustomerService.create(sales_user, data, mock_db)

        mock_create.assert_called_once_with(
            salesperson_id=sales_user.id,
            company_vat=existing_company.vat_number,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            db=mock_db,
        )

    def test_create_uses_auto_created_company_vat(self, mock_db):
        """When the company is auto-created, the new company's vat_number must be used."""
        sales_user = UserFactory(role=Roles.SALES)
        new_company = CompanyFactory(vat_number=VAT_NUMBER)
        data = self._make_data(company_vat=VAT_NUMBER)
        created_customer = CustomerFactory()

        with (
            patch.object(CompanyService, "get_by_vat", return_value=None),
            patch.object(CompanyService, "create", return_value=new_company),
            patch.object(Customer, "create", return_value=created_customer) as mock_create,
        ):
            CustomerService.create(sales_user, data, mock_db)

        _, kwargs = mock_create.call_args
        assert kwargs["company_vat"] == new_company.vat_number


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_update_returns_updated_customer(self, mock_db):
        target = CustomerFactory()
        data = CustomerUpdateInput(first_name="Updated")
        updated_customer = CustomerFactory(first_name="Updated")

        with patch.object(Customer, "update", return_value=updated_customer):
            result = CustomerService.update(target, data, mock_db)

        assert result == updated_customer

    def test_update_calls_update_on_target(self, mock_db):
        target = CustomerFactory()
        data = CustomerUpdateInput(first_name="Updated")

        target.update = MagicMock(return_value=target)

        CustomerService.update(target, data, mock_db)

        target.update.assert_called_once_with(data, mock_db)

    def test_update_any_role_can_call_service(self, mock_db):
        """The service itself has no role check — that is the controller's responsibility."""
        target = CustomerFactory()
        data = CustomerUpdateInput(last_name="Smith")

        target.update = MagicMock(return_value=target)

        # Should not raise regardless of who calls it
        CustomerService.update(target, data, mock_db)

        target.update.assert_called_once()


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_delete_calls_delete_on_target(self, mock_db):
        """Customer.delete() must be called on the target."""
        target = CustomerFactory()
        target.delete = MagicMock()

        with (
            patch.object(Customer, "get_all_by_company_vat", return_value=[]),
            patch.object(Company, "delete_by_vat"),
        ):
            CustomerService.delete(target, mock_db)

        target.delete.assert_called_once_with(mock_db)

    def test_delete_removes_orphan_company(self, mock_db):
        """When no other customer shares the company, delete_by_vat must be called."""
        target = CustomerFactory()
        target.delete = MagicMock()

        with (
            patch.object(Customer, "get_all_by_company_vat", return_value=[]) as mock_remaining,
            patch.object(Company, "delete_by_vat") as mock_delete_company,
        ):
            CustomerService.delete(target, mock_db)

        mock_remaining.assert_called_once_with(target.company_vat, mock_db)
        mock_delete_company.assert_called_once_with(target.company_vat, mock_db)

    def test_delete_keeps_company_when_other_customers_exist(self, mock_db):
        """When other customers share the company, delete_by_vat must NOT be called."""
        target = CustomerFactory()
        other_customer = CustomerFactory(company_vat=target.company_vat)
        target.delete = MagicMock()

        with (
            patch.object(Customer, "get_all_by_company_vat", return_value=[other_customer]),
            patch.object(Company, "delete_by_vat") as mock_delete_company,
        ):
            CustomerService.delete(target, mock_db)

        mock_delete_company.assert_not_called()

    def test_delete_returns_none(self, mock_db):
        target = CustomerFactory()
        target.delete = MagicMock()

        with (
            patch.object(Customer, "get_all_by_company_vat", return_value=[]),
            patch.object(Company, "delete_by_vat"),
        ):
            result = CustomerService.delete(target, mock_db)

        assert result is None
