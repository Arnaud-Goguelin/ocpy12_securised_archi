from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.errors import UserIsNotOwnerError
from crm_epic_events.permissions import Permissions, Roles, require_roles
from crm_epic_events.services import ContractService, CustomerService, UserService
from crm_epic_events.services.contract.schemas import ContractCreateInput, ContractUpdateInput
from crm_epic_events.utils import check_choice
from crm_epic_events.utils.constants import MenuItem, NavSignal, StandardInputs
from crm_epic_events.utils.printers import print_error, print_success, print_validation_errors
from crm_epic_events.views import ContractView, MainMenuView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User


class ContractController(BaseController):
    """Handles navigation and user interactions for contract management."""

    def __init__(self, db: "Session", user: "User | None"):
        self.db = db
        self.user = user
        self.view = ContractView()
        self.menu_items = [
            MenuItem(
                "1",
                "List my contracts" if self.user.role == Roles.SALES else "List all contracts",
                self.handle_list,
            ),
            MenuItem("2", "List unsigned contracts", self.handle_list_unsigned),
            MenuItem("3", "List unpaid contracts", self.handle_list_unpaid),
            MenuItem("4", "Create a contract", self.handle_create, [*Permissions.CONTRACT_CREATE]),
            MenuItem("5", "Update a contract", self.handle_update, [*Permissions.CONTRACT_UPDATE]),
            MenuItem("6", "Delete a contract", self.handle_delete, [*Permissions.CONTRACT_DELETE]),
            MenuItem(StandardInputs.CANCELLED, "Back to main menu", self.handle_back),
        ]

    def handle_contracts_menu(self) -> NavSignal:
        """Runs the contract sub-menu loop, dispatching to the selected action until the user navigates back."""

        while True:
            choice = MainMenuView.display(self.visible_menu_items)
            item = check_choice(choice, self.visible_menu_items)
            if item is None:
                continue
            signal = item.action()
            if signal == NavSignal.BACK:
                return NavSignal.BACK

    # --- Handlers ---

    def handle_list(self) -> NavSignal:
        contracts = ContractService.get_all(self.db)
        self.view.display_contracts(contracts, title="All contracts")
        return NavSignal.STAY

    def handle_list_unsigned(self) -> NavSignal:
        contracts = ContractService.get_unsigned(self.db)
        self.view.display_contracts(contracts, title="Unsigned contracts")
        return NavSignal.STAY

    def handle_list_unpaid(self) -> NavSignal:
        contracts = ContractService.get_unpaid(self.db)
        self.view.display_contracts(contracts, title="Unpaid contracts")
        return NavSignal.STAY

    @require_roles(*Permissions.CONTRACT_CREATE)
    def handle_create(self) -> NavSignal:
        """
        Prompts for a customer and financial details, then creates a new contract. Restricted to MANAGER only.

        The salesperson is automatically inherited from the selected customer.

        Raises:
            ValidationError: If the input does not pass Pydantic validation (e.g. remaining > total).
        """

        customers = CustomerService.get_all(self.db)
        salespersons = UserService.get_all_by_role(Roles.SALES, self.db)

        if not customers:
            print_error("No customers found. Please create a customer first.")
            return NavSignal.STAY

        raw_customer, raw_salesperson, raw_data = self.view.prompt_create(customers, salespersons)

        try:
            customer = customers[int(raw_customer) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw_customer}'")
            return NavSignal.STAY

        try:
            salesperson = salespersons[int(raw_salesperson) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw_salesperson}'")
            return NavSignal.STAY

        try:
            data = ContractCreateInput(customer_id=customer.id, salesperson_id=salesperson.id, **raw_data)
            contract = ContractService.create(customer, data, self.db)
            print_success(f"Contract '{contract.id}' created successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        return NavSignal.STAY

    @require_roles(*Permissions.CONTRACT_UPDATE)
    def handle_update(self) -> NavSignal:
        """
        Lets the current user select and update a contract.

        Managers see all contracts; salespersons only see their own.
        Ownership is enforced before the update is applied.

        Raises:
            ValidationError: If the updated input does not pass Pydantic validation.
            UserIsNotOwnerError: If the current user is not the assigned salesperson of the target contract.
        """

        contracts = (
            ContractService.get_all(self.db)
            if self.user.role == Roles.MANAGER
            else ContractService.get_all_by_salesperson(self.user, self.db)
        )
        raw = self.view.prompt_select_contract(contracts)
        if raw == StandardInputs.CANCELLED:
            return NavSignal.STAY
        try:
            target = contracts[int(raw) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw}'")
            return NavSignal.STAY

        self.check_ownership(target.salesperson)

        raw_update = self.view.prompt_update(target)
        if not raw_update:
            print_success("Nothing to update.")
            return NavSignal.STAY

        try:
            data = ContractUpdateInput(**raw_update)
            ContractService.update(target, data, self.db)
            print_success("Contract updated successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except UserIsNotOwnerError as error:
            print_error(error.message)
        return NavSignal.STAY

    @require_roles(*Permissions.CONTRACT_DELETE)
    def handle_delete(self) -> NavSignal:
        """
        Lets a MANAGER select and delete a contract. Restricted to MANAGER only.
        """
        contracts = ContractService.get_all(self.db)
        raw = self.view.prompt_select_contract(contracts)
        if raw == StandardInputs.CANCELLED:
            return NavSignal.STAY
        try:
            target = contracts[int(raw) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw}'")
            return NavSignal.STAY

        ContractService.delete(target, self.db)
        print_success(f"Contract '{target.id}' deleted.")
        return NavSignal.STAY

    @staticmethod
    def handle_back() -> NavSignal:
        return NavSignal.BACK
