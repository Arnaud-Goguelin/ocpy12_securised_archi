import uuid

from unittest.mock import MagicMock, patch

from crm_epic_events.models.contract import Contract
from crm_epic_events.services.contract.schemas import ContractCreateInput, ContractUpdateInput
from crm_epic_events.services.contract.service import ContractService
from crm_epic_events.utils import Roles
from tests.factories import ContractFactory, CustomerFactory, UserFactory


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_get_all_returns_contracts(self, mock_db):
        contracts = ContractFactory.build_batch(3)
        with patch.object(Contract, "get_all", return_value=contracts):
            result = ContractService.get_all(mock_db)

        assert result == contracts

    def test_get_all_returns_empty_list(self, mock_db):
        with patch.object(Contract, "get_all", return_value=[]):
            result = ContractService.get_all(mock_db)

        assert result == []


# ── get_by_id ─────────────────────────────────────────────────────────────────


class TestGetById:
    def test_returns_contract_when_found(self, mock_db):
        contract = ContractFactory()
        with patch.object(Contract, "get_by_id", return_value=contract):
            result = ContractService.get_by_id(contract.id, mock_db)

        assert result == contract

    def test_returns_none_when_not_found(self, mock_db):
        with patch.object(Contract, "get_by_id", return_value=None):
            result = ContractService.get_by_id(str(uuid.uuid4()), mock_db)

        assert result is None

    def test_passes_correct_id_to_model(self, mock_db):
        contract_id = str(uuid.uuid4())
        with patch.object(Contract, "get_by_id", return_value=None) as mock_get:
            ContractService.get_by_id(contract_id, mock_db)

        mock_get.assert_called_once_with(contract_id, mock_db)


# ── get_all_by_salesperson ────────────────────────────────────────────────────


class TestGetAllBySalesperson:
    def test_returns_contracts_for_salesperson(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        contracts = ContractFactory.build_batch(2, salesperson_id=sales_user.id)

        with patch.object(Contract, "get_all_by_salesperson", return_value=contracts):
            result = ContractService.get_all_by_salesperson(sales_user, mock_db)

        assert result == contracts

    def test_returns_empty_list_when_no_contracts(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)

        with patch.object(Contract, "get_all_by_salesperson", return_value=[]):
            result = ContractService.get_all_by_salesperson(sales_user, mock_db)

        assert result == []

    def test_passes_salesperson_id_to_model(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)

        with patch.object(Contract, "get_all_by_salesperson", return_value=[]) as mock_get:
            ContractService.get_all_by_salesperson(sales_user, mock_db)

        mock_get.assert_called_once_with(sales_user.id, mock_db)


# ── get_unsigned ──────────────────────────────────────────────────────────────


class TestGetUnsigned:
    def test_returns_unsigned_contracts(self, mock_db):
        contracts = ContractFactory.build_batch(2, status=False)

        with patch.object(Contract, "get_unsigned", return_value=contracts):
            result = ContractService.get_unsigned(mock_db)

        assert result == contracts
        assert all(not c.status for c in result)

    def test_returns_empty_list_when_all_signed(self, mock_db):
        with patch.object(Contract, "get_unsigned", return_value=[]):
            result = ContractService.get_unsigned(mock_db)

        assert result == []


# ── get_unpaid ────────────────────────────────────────────────────────────────


class TestGetUnpaid:
    def test_returns_unpaid_contracts(self, mock_db):
        contracts = ContractFactory.build_batch(2, remaining_amount=500.0)

        with patch.object(Contract, "get_unpaid", return_value=contracts):
            result = ContractService.get_unpaid(mock_db)

        assert result == contracts
        assert all(c.remaining_amount > 0 for c in result)

    def test_returns_empty_list_when_all_paid(self, mock_db):
        with patch.object(Contract, "get_unpaid", return_value=[]):
            result = ContractService.get_unpaid(mock_db)

        assert result == []


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def _make_data(self, **kwargs) -> ContractCreateInput:
        data = ContractCreateInput(
            customer_id=str(uuid.uuid4()),
            total_amount=1000.0,
            remaining_amount=500.0,
            status=False,
        )
        if kwargs:
            data = data.model_copy(update=kwargs)
        return data

    def test_create_returns_contract(self, mock_db):
        customer = CustomerFactory()
        data = self._make_data(customer_id=customer.id)
        created_contract = ContractFactory()

        with patch.object(Contract, "create", return_value=created_contract):
            result = ContractService.create(customer, data, mock_db)

        assert result == created_contract

    def test_create_passes_correct_args_to_model(self, mock_db):
        customer = CustomerFactory()
        data = self._make_data(customer_id=customer.id)
        created_contract = ContractFactory()

        with patch.object(Contract, "create", return_value=created_contract) as mock_create:
            ContractService.create(customer, data, mock_db)

        mock_create.assert_called_once_with(
            customer_id=data.customer_id,
            salesperson_id=customer.salesperson_id,
            total_amount=data.total_amount,
            remaining_amount=data.remaining_amount,
            status=data.status,
            db=mock_db,
        )

    def test_create_inherits_salesperson_from_customer(self, mock_db):
        customer = CustomerFactory()
        data = self._make_data(customer_id=customer.id)
        created_contract = ContractFactory(salesperson_id=customer.salesperson_id)

        with patch.object(Contract, "create", return_value=created_contract) as mock_create:
            ContractService.create(customer, data, mock_db)

        _, kwargs = mock_create.call_args
        assert kwargs["salesperson_id"] == customer.salesperson_id

    def test_create_any_role_can_call_service(self, mock_db):
        """The service has no role check — that is the controller's responsibility."""
        customer = CustomerFactory()
        data = self._make_data(customer_id=customer.id)
        created_contract = ContractFactory()

        with patch.object(Contract, "create", return_value=created_contract):
            # Should not raise regardless of role
            result = ContractService.create(customer, data, mock_db)

        assert result == created_contract


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_update_returns_updated_contract(self, mock_db):
        target = ContractFactory()
        data = ContractUpdateInput(remaining_amount=0.0)
        updated_contract = ContractFactory(remaining_amount=0.0)

        with patch.object(Contract, "update", return_value=updated_contract):
            result = ContractService.update(target, data, mock_db)

        assert result == updated_contract

    def test_update_calls_update_on_target(self, mock_db):
        target = ContractFactory()
        data = ContractUpdateInput(status=True)
        target.update = MagicMock(return_value=target)

        ContractService.update(target, data, mock_db)

        target.update.assert_called_once_with(data, mock_db)

    def test_update_any_role_can_call_service(self, mock_db):
        """The service itself has no role check — that is the controller's responsibility."""
        target = ContractFactory()
        data = ContractUpdateInput(total_amount=2000.0)
        target.update = MagicMock(return_value=target)

        ContractService.update(target, data, mock_db)

        target.update.assert_called_once()


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_delete_calls_delete_on_target(self, mock_db):
        target = ContractFactory()
        target.delete = MagicMock(return_value=None)

        ContractService.delete(target, mock_db)

        target.delete.assert_called_once_with(mock_db)

    def test_delete_returns_none(self, mock_db):
        target = ContractFactory()

        with patch.object(Contract, "delete", return_value=None):
            result = ContractService.delete(target, mock_db)

        assert result is None
