from typing import TYPE_CHECKING

from crm_epic_events.utils import StandardInputs
from crm_epic_events.utils.printers import print_info, print_option, print_title, prompt


if TYPE_CHECKING:
    from crm_epic_events.models import Contract, Customer, User


class ContractView:
    """Handles all CLI prompts and display output for contracts operations."""

    # --- Prompts ---

    @staticmethod
    def prompt_create(customers: list["Customer"], salepersons: list["User"]) -> tuple[str, str, dict]:
        print_title("Create new contract")

        for i, customer in enumerate(customers, start=1):
            print_option(str(i), f"{customer.first_name} {customer.last_name}  |  {customer.email}")
        raw_customer = prompt("Select a customer").strip()

        for i, saleperson in enumerate(salepersons, start=1):
            print_option(str(i), f"{saleperson.first_name} {saleperson.last_name}  |  {saleperson.email}")
        raw_saleperson = prompt("Select a salesperson").strip()

        return (
            raw_customer,
            raw_saleperson,
            {
                "total_amount": prompt("Total amount").strip(),
                "remaining_amount": prompt("Remaining amount").strip(),
                "status": prompt(f"Already signed? ({StandardInputs.VALIDATION}/{StandardInputs.CANCELLED})")
                .strip()
                .lower()
                == StandardInputs.VALIDATION,
            },
        )

    @staticmethod
    def prompt_update(target: "Contract") -> dict:
        print_title(f"Update contract — {target.id}")
        print_info("Leave blank to keep current value.")
        data = {}

        raw_total = prompt(f"Total amount (current: {target.total_amount})").strip()
        if raw_total:
            data["total_amount"] = raw_total

        raw_remaining = prompt(f"Remaining amount (current: {target.remaining_amount})").strip()
        if raw_remaining:
            data["remaining_amount"] = raw_remaining

        raw_status = prompt(f"Signed? (current: {'Yes' if target.status else 'No'}) (y/n)").strip().lower()
        if raw_status in (StandardInputs.VALIDATION, StandardInputs.CANCELLED):
            data["status"] = raw_status == StandardInputs.VALIDATION

        return data

    @staticmethod
    def prompt_select_contract(contracts: list["Contract"]) -> str:
        for i, contract in enumerate(contracts, start=1):
            print_option(
                str(i),
                f"ID: {contract.id}  |  Customer: {contract.customer.first_name} {contract.customer.last_name}"
                f"  |  Total: {contract.total_amount}  |  Remaining: {contract.remaining_amount}"
                f"  |  Signed: {'Yes' if contract.status else 'No'}",
            )
        print_option(StandardInputs.CANCELLED, "Cancel")
        return prompt("Select a contract").strip().upper()

    # --- Display ---

    @staticmethod
    def display_contracts(contracts: list["Contract"], title: str = "Contracts") -> None:
        print_title(title)
        if not contracts:
            print_info("No contracts found.")
            return
        for contract in contracts:
            print_info(
                f"  ID: {contract.id}"
                f"  |  Customer: {contract.customer.first_name} {contract.customer.last_name}"
                f"  |  Salesperson: {contract.salesperson.first_name} {contract.salesperson.last_name} "
                f"{contract.salesperson.id}"
                f"  |  Total: {contract.total_amount:.2f}"
                f"  |  Remaining: {contract.remaining_amount:.2f}"
                f"  |  Signed: {'Yes' if contract.status else 'No'}"
                f"  |  Created: {contract.created_at.strftime('%Y-%m-%d')}"
            )
