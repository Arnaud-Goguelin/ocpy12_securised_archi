from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.errors import UserIsNotOwnerError, UserNotAllowedError
from crm_epic_events.permissions import require_roles
from crm_epic_events.services import ContractService
from crm_epic_events.services.contract.schemas import ContractCreateInput, ContractUpdateInput
from crm_epic_events.utils import check_choice
from crm_epic_events.utils.constants import MenuItem, NavSignal, Roles, StandardInputs
from crm_epic_events.utils.printers import print_error, print_success, print_validation_errors
from crm_epic_events.views import ContractView, MainMenuView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User


class ContractController(BaseController):
    def __init__(self, db: "Session", user: "User | None"):
        self.db = db
        self.user = user
        self.view = ContractView()
        self.menu_items = [
            MenuItem("1", "List all contracts", self.handle_list),
            MenuItem("2", "List unsigned contracts", self.handle_list_unsigned, [Roles.MANAGER, Roles.SALES]),
            MenuItem("3", "List unpaid contracts", self.handle_list_unpaid, [Roles.MANAGER, Roles.SALES]),
            MenuItem("4", "List my contracts", self.handle_list_mine, [Roles.SALES]),
            MenuItem("5", "Create a contract", self.handle_create, [Roles.MANAGER]),
            MenuItem("6", "Update a contract", self.handle_update, [Roles.MANAGER, Roles.SALES]),
            MenuItem("7", "Delete a contract", self.handle_delete, [Roles.MANAGER]),
            MenuItem(StandardInputs.CANCELLED, "Back to main menu", self.handle_back),
        ]

    def handle_contracts_menu(self) -> NavSignal:
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

    @require_roles(Roles.SALES)
    def handle_list_mine(self) -> NavSignal:
        contracts = ContractService.get_all_by_salesperson(self.user, self.db)
        self.view.display_contracts(contracts, title="My contracts")
        return NavSignal.STAY

    @require_roles(Roles.MANAGER)
    def handle_create(self) -> NavSignal:
        from crm_epic_events.services import CustomerService

        customers = CustomerService.get_all(self.db)
        if not customers:
            print_error("No customers found. Please create a customer first.")
            return NavSignal.STAY

        try:
            raw = self.view.prompt_create(customers)
            data = ContractCreateInput(**raw)
            contract = ContractService.create(self.user, data, self.db)
            print_success(f"Contract '{contract.id}' created successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except (UserNotAllowedError, ValueError) as error:
            print_error(str(error) if isinstance(error, ValueError) else error.message)
        return NavSignal.STAY

    @require_roles(Roles.MANAGER, Roles.SALES)
    def handle_update(self) -> NavSignal:
        # SALES can only update contracts linked to their own customers
        contracts = (
            ContractService.get_all(self.db)
            if self.user.role == Roles.MANAGER
            else ContractService.get_all_by_salesperson(self.user, self.db)
        )

        try:
            target = self.view.prompt_select_contract(contracts)
        except ValueError as error:
            print_error(str(error))
            return NavSignal.STAY

        if target is None:
            return NavSignal.STAY

        self.check_ownership(target.salesperson)

        raw = self.view.prompt_update(target)
        if not raw:
            print_success("Nothing to update.")
            return NavSignal.STAY

        try:
            data = ContractUpdateInput(**raw)
            ContractService.update(target, data, self.db)
            print_success("Contract updated successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except UserIsNotOwnerError as error:
            print_error(error.message)
        return NavSignal.STAY

    @require_roles(Roles.MANAGER)
    def handle_delete(self) -> NavSignal:
        contracts = ContractService.get_all(self.db)

        try:
            target = self.view.prompt_select_contract(contracts)
        except ValueError as error:
            print_error(str(error))
            return NavSignal.STAY

        if target is None:
            return NavSignal.STAY

        try:
            ContractService.delete(target, self.db)
            print_success(f"Contract '{target.id}' deleted.")
        except UserNotAllowedError as error:
            print_error(error.message)
        return NavSignal.STAY

    @staticmethod
    def handle_back() -> NavSignal:
        return NavSignal.BACK
