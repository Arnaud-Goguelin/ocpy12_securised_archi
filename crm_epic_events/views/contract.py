from typing import TYPE_CHECKING

from crm_epic_events.utils.printers import print_info, print_option, print_title, prompt


if TYPE_CHECKING:
    from crm_epic_events.models import Contract, Customer


class ContractView:
    # --- Prompts ---

    @staticmethod
    def prompt_create(customers: list["Customer"]) -> dict:
        print_title("Create new contract")
        for i, customer in enumerate(customers, start=1):
            print_option(str(i), f"{customer.first_name} {customer.last_name}  |  {customer.email}")
        raw = prompt("Select a customer").strip()
        try:
            customer = customers[int(raw) - 1]
        except (ValueError, IndexError):
            raise ValueError(f"Invalid selection: '{raw}'") from None

        return {
            "customer_id": customer.id,
            "total_amount": prompt("Total amount").strip(),  # return a str but Pydantic will convert it to Decimal
            "remaining_amount": prompt("Total amount").strip(),
            "status": prompt("Already signed? (y/N)").strip().lower() == "y",
        }

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
        if raw_status in ("y", "n"):
            data["status"] = raw_status == "y"

        return data

    @staticmethod
    def prompt_select_contract(contracts: list["Contract"]) -> "Contract | None":
        for i, contract in enumerate(contracts, start=1):
            print_option(
                str(i),
                f"ID: {contract.id[:8]}…  |  Customer: {contract.customer_id}"
                f"  |  Total: {contract.total_amount}  |  Remaining: {contract.remaining_amount}"
                f"  |  Signed: {'Yes' if contract.status else 'No'}",
            )
        print_option("Q", "Cancel")
        raw = prompt("Select a contract").strip().upper()
        if raw == "Q":
            return None
        try:
            return contracts[int(raw) - 1]
        except (ValueError, IndexError):
            raise ValueError(f"Invalid selection: '{raw}'") from None

    # --- Display ---

    @staticmethod
    def display_contracts(contracts: list["Contract"], title: str = "Contracts") -> None:
        print_title(title)
        if not contracts:
            print_info("No contracts found.")
            return
        for contract in contracts:
            print_info(
                f"  ID: {contract.id[:8]}…"
                f"  |  Customer: {contract.customer_id}"
                f"  |  Salesperson: {contract.salesperson_id}"
                f"  |  Total: {contract.total_amount:.2f}"
                f"  |  Remaining: {contract.remaining_amount:.2f}"
                f"  |  Signed: {'Yes' if contract.status else 'No'}"
                f"  |  Created: {contract.created_at.strftime('%Y-%m-%d')}"
            )
