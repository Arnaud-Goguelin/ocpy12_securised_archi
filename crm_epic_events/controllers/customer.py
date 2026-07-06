from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.errors import UserIsNotOwnerError, UserNotAllowedError
from crm_epic_events.permissions import require_roles
from crm_epic_events.services import CustomerService
from crm_epic_events.services.customer.schemas import CustomerCreateInput, CustomerUpdateInput
from crm_epic_events.utils import check_choice
from crm_epic_events.utils.constants import MenuItem, NavSignal, Roles, StandardInputs
from crm_epic_events.utils.printers import print_error, print_success, print_validation_errors
from crm_epic_events.views import CustomerView, MainMenuView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User


class CustomerController(BaseController):
    def __init__(self, db: "Session", user: "User | None"):
        self.db = db
        self.user = user
        self.view = CustomerView()
        self.menu_items = [
            MenuItem("1", "List all customers", self.handle_list),
            MenuItem("2", "List my customers", self.handle_list_mine, [Roles.SALES]),
            MenuItem("3", "Create a customer", self.handle_create, [Roles.SALES]),
            MenuItem("4", "Update a customer", self.handle_update, [Roles.MANAGER, Roles.SALES]),
            MenuItem("5", "Delete a customer", self.handle_delete, [Roles.MANAGER]),
            MenuItem(StandardInputs.CANCELLED, "Back to main menu", self.handle_back),
        ]

    def handle_customers_menu(self) -> NavSignal:
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
        customers = CustomerService.get_all(self.db)
        self.view.display_customers(customers, title="All customers")
        return NavSignal.STAY

    @require_roles(Roles.SALES)
    def handle_create(self) -> NavSignal:
        raw = self.view.prompt_create()
        try:
            data = CustomerCreateInput(**raw)
            customer = CustomerService.create(self.user, data, self.db)
            print_success(f"Customer '{customer.first_name} {customer.last_name}' created successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except UserNotAllowedError as error:
            print_error(error.message)
        return NavSignal.STAY

    @require_roles(Roles.MANAGER, Roles.SALES)
    def handle_update(self) -> NavSignal:

        # improve app perf by filtering result by salesperson if user is not manager
        # and also allow self.user to update its own customers only if it is not manager
        customers = (
            CustomerService.get_all(self.db)
            if self.user.role == Roles.MANAGER
            else CustomerService.get_all_by_salesperson(self.user, self.db)
        )

        raw = self.view.prompt_select_customer(customers)
        if raw == StandardInputs.CANCELLED:
            return NavSignal.STAY
        try:
            target = customers[int(raw) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw}'")
            return NavSignal.STAY

        if target is None:
            return NavSignal.STAY

        # this check is redundant because if self.user is not manager we have already filter
        # customers by salesperson
        # its just show both way to check at if
        self.check_ownership(target.salesperson)

        raw = self.view.prompt_update(target)
        if not raw:
            print_success("Nothing to update.")
            return NavSignal.STAY

        try:
            data = CustomerUpdateInput(**raw)
            CustomerService.update(target, data, self.db)
            print_success("Customer updated successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except UserIsNotOwnerError as error:
            print_error(error.message)
        return NavSignal.STAY

    @require_roles(Roles.MANAGER)
    def handle_delete(self) -> NavSignal:
        customers = CustomerService.get_all(self.db)
        try:
            target = self.view.prompt_select_customer(customers)
        except ValueError as error:
            print_error(str(error))
            return NavSignal.STAY

        if target is None:
            return NavSignal.STAY

        # no ownship check needed here, since only the manager can delete a customer

        try:
            CustomerService.delete(target, self.db)
            print_success(f"Customer '{target.first_name} {target.last_name}' deleted.")
        except UserNotAllowedError as error:
            print_error(error.message)
        return NavSignal.STAY

    @staticmethod
    def handle_back() -> NavSignal:
        return NavSignal.BACK
