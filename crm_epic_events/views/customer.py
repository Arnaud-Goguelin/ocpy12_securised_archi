from typing import TYPE_CHECKING

from crm_epic_events.utils import StandardInputs
from crm_epic_events.utils.printers import print_info, print_option, print_title, prompt


if TYPE_CHECKING:
    from crm_epic_events.models import Customer


class CustomerView:
    # --- Prompts ---

    @staticmethod
    def prompt_create() -> dict:
        print_title("Create new customer")
        return {
            "first_name": prompt("First name").strip(),
            "last_name": prompt("Last name").strip(),
            "email": prompt("Email").strip(),
            "phone": prompt("Phone").strip(),
            "company_vat": prompt("Company VAT number").strip(),
            "company_name": prompt("Company name (created if not found)").strip(),
        }

    @staticmethod
    def prompt_update(target: "Customer") -> dict:
        print_title(f"Update customer — {target.first_name} {target.last_name}")
        print_info("Leave blank to keep current value.")
        data = {}
        for field_name, current in [
            ("first_name", target.first_name),
            ("last_name", target.last_name),
            ("email", target.email),
            ("phone", target.phone),
        ]:
            value = prompt(f"{field_name.replace('_', ' ').title()} (current: {current})").strip()
            if value:
                data[field_name] = value
        return data

    @staticmethod
    def prompt_select_customer(customers: list["Customer"]) -> str:
        """Displays a numbered list and returns the raw input string."""
        for i, customer in enumerate(customers, start=1):
            print_option(
                str(i),
                f"{customer.first_name} {customer.last_name}  |  {customer.email}  |  {customer.company_vat}",
            )
        print_option(StandardInputs.CANCELLED, "Cancel")
        return prompt("Select a customer").strip().upper()

    # --- Display ---

    @staticmethod
    def display_customers(customers: list["Customer"], title: str = "Customers") -> None:
        print_title(title)
        if not customers:
            print_info("No customers found.")
            return
        for customer in customers:
            print_info(
                f"  {customer.first_name} {customer.last_name}"
                f"  |  {customer.email}"
                f"  |  {customer.phone}"
                f"  |  VAT: {customer.company_vat}"
                f"  |  updated: {customer.updated_at.strftime('%Y-%m-%d')}"
            )
