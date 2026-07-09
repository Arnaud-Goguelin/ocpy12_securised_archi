from typing import TYPE_CHECKING

from crm_epic_events.utils import StandardInputs
from crm_epic_events.utils.printers import print_info, print_option, print_title, prompt


if TYPE_CHECKING:
    from crm_epic_events.models import Company


class CompanyView:
    """Handles all CLI prompts and display output for company operations."""

    # --- Prompts ---

    @staticmethod
    def prompt_create() -> dict:
        print_title("Create new company")
        return {
            "vat_number": prompt("VAT number").strip(),
            "name": prompt("Company name").strip(),
        }

    @staticmethod
    def prompt_update(target: "Company") -> dict:
        print_title(f"Update company — {target.name}")
        print_info("Leave blank to keep current value.")
        value = prompt(f"Company name (current: {target.name})").strip()
        return {"name": value} if value else {}

    @staticmethod
    def prompt_select_company(companies: list["Company"]) -> str:
        for i, company in enumerate(companies, start=1):
            print_option(str(i), f"{company.name}  |  VAT: {company.vat_number}")
        print_option(StandardInputs.CANCELLED, "Cancel")
        return prompt("Select a company").strip().upper()

    # --- Display ---

    @staticmethod
    def display_companies(companies: list["Company"], title: str = "Companies") -> None:
        print_title(title)
        if not companies:
            print_info("No companies found.")
            return
        for company in companies:
            print_info(f"  {company.name}  |  VAT: {company.vat_number}")
