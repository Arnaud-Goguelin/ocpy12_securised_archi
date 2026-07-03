from typing import TYPE_CHECKING

from crm_epic_events.models import Contract
from crm_epic_events.utils import db_transaction


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import Customer, User
    from crm_epic_events.services.contract.schemas import ContractCreateInput, ContractUpdateInput


class ContractService:
    @staticmethod
    def get_all(db: "Session") -> list["Contract"]:
        return Contract.get_all(db)

    @staticmethod
    def get_by_id(contract_id: str, db: "Session") -> "Contract | None":
        return Contract.get_by_id(contract_id, db)

    @staticmethod
    def get_all_by_salesperson(salesperson: "User", db: "Session") -> list["Contract"]:
        return Contract.get_all_by_salesperson(salesperson.id, db)

    @staticmethod
    def get_unsigned(db: "Session") -> list["Contract"]:
        return Contract.get_unsigned(db)

    @staticmethod
    def get_unpaid(db: "Session") -> list["Contract"]:
        return Contract.get_unpaid(db)

    @staticmethod
    def create(
        customer: "Customer",
        data: "ContractCreateInput",
        db: "Session",
    ) -> "Contract":
        """Only MANAGER can create contracts. Salesperson is inherited from the customer."""
        with db_transaction(db, "Creating contract"):
            return Contract.create(
                customer_id=customer.id,
                salesperson_id=customer.salesperson_id,
                total_amount=data.total_amount,
                remaining_amount=data.remaining_amount,
                status=data.status,
                db=db,
            )

    @staticmethod
    def update(
        target_contract: "Contract",
        data: "ContractUpdateInput",
        db: "Session",
    ) -> "Contract":
        with db_transaction(db, "Updating contract"):
            return target_contract.update(data, db)

    @staticmethod
    def delete(target_contract: "Contract", db: "Session") -> None:
        with db_transaction(db, "Deleting contract"):
            target_contract.delete(db)
