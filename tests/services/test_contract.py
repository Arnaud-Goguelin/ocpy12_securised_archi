import uuid

from decimal import Decimal

from crm_epic_events.services.contract.schemas import ContractUpdateInput
from crm_epic_events.services.contract.service import ContractService
from tests.factories import ContractDBFactory


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_returns_all_contracts(self, db_session):
        ContractDBFactory.create_batch(3)
        result = ContractService.get_all(db_session)
        assert len(result) == 3

    def test_returns_empty_list(self, db_session):
        result = ContractService.get_all(db_session)
        assert result == []


# ── get_by_id ─────────────────────────────────────────────────────────────────


class TestGetById:
    def test_returns_contract_when_found(self, db_session, signed_contract):
        result = ContractService.get_by_id(signed_contract.id, db_session)
        assert result is not None
        assert result.id == signed_contract.id

    def test_returns_none_when_not_found(self, db_session):
        result = ContractService.get_by_id(uuid.uuid4(), db_session)
        assert result is None


# ── get_all_by_salesperson ────────────────────────────────────────────────────


class TestGetAllBySalesperson:
    def test_returns_contracts_for_salesperson(self, db_session, signed_contract):
        salesperson = signed_contract.salesperson
        result = ContractService.get_all_by_salesperson(salesperson, db_session)
        assert len(result) == 1
        assert result[0].id == signed_contract.id

    def test_returns_empty_list_when_no_contracts(self, db_session, salesperson):
        result = ContractService.get_all_by_salesperson(salesperson, db_session)
        assert result == []


# ── get_unsigned ──────────────────────────────────────────────────────────────


class TestGetUnsigned:
    def test_returns_only_unsigned_contracts(self, db_session, unsigned_contract, signed_contract):
        result = ContractService.get_unsigned(db_session)
        assert len(result) == 1
        assert result[0].id == unsigned_contract.id

    def test_returns_empty_when_all_signed(self, db_session, signed_contract):
        result = ContractService.get_unsigned(db_session)
        assert result == []


# ── get_unpaid ────────────────────────────────────────────────────────────────


class TestGetUnpaid:
    def test_returns_only_unpaid_contracts(self, db_session):
        ContractDBFactory(remaining_amount=Decimal("200.00"))
        ContractDBFactory(remaining_amount=Decimal("0.00"))
        result = ContractService.get_unpaid(db_session)
        assert len(result) == 1
        assert result[0].remaining_amount > 0

    def test_returns_empty_when_all_paid(self, db_session):
        ContractDBFactory(remaining_amount=Decimal("0.00"))
        result = ContractService.get_unpaid(db_session)
        assert result == []


# ── create ────────────────────────────────────────────────────────────────────


class TestCreate:
    def test_creates_and_returns_contract(self, db_session, salesperson, customer, contract_create_data):
        contract = ContractService.create(customer, contract_create_data, db_session)
        assert contract.id is not None
        assert contract.total_amount == Decimal("1000.00")
        assert contract.remaining_amount == Decimal("500.00")

    def test_inherits_salesperson_from_customer(self, db_session, customer, contract_create_data):
        contract = ContractService.create(customer, contract_create_data, db_session)
        assert contract.salesperson_id == customer.salesperson_id

    def test_contract_is_persisted(self, db_session, customer, contract_create_data):
        contract = ContractService.create(customer, contract_create_data, db_session)
        assert ContractService.get_by_id(contract.id, db_session) is not None


# ── update ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_updates_remaining_amount(self, db_session):
        contract = ContractDBFactory(remaining_amount=Decimal("500.00"))
        data = ContractUpdateInput(remaining_amount=Decimal("0.00"))
        updated = ContractService.update(contract, data, db_session)
        assert updated.remaining_amount == Decimal("0.00")

    def test_updates_status(self, db_session):
        contract = ContractDBFactory(status=False)
        data = ContractUpdateInput(status=True)
        updated = ContractService.update(contract, data, db_session)
        assert updated.status is True

    def test_partial_update_does_not_affect_other_fields(self, db_session):
        contract = ContractDBFactory(total_amount=Decimal("1000.00"), status=False)
        data = ContractUpdateInput(status=True)
        updated = ContractService.update(contract, data, db_session)
        assert updated.total_amount == Decimal("1000.00")


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_deletes_contract(self, db_session):
        contract = ContractDBFactory()
        contract_id = contract.id
        ContractService.delete(contract, db_session)
        assert ContractService.get_by_id(contract_id, db_session) is None

    def test_delete_returns_none(self, db_session):
        contract = ContractDBFactory()
        result = ContractService.delete(contract, db_session)
        assert result is None
