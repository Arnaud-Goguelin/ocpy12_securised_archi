from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.errors import UserIsNotOwnerError, UserNotAllowedError
from crm_epic_events.permissions import Permissions, Roles, require_roles
from crm_epic_events.services import CustomerService
from crm_epic_events.services.customer.schemas import CustomerCreateInput, CustomerUpdateInput
from crm_epic_events.utils import check_choice
from crm_epic_events.utils.constants import MenuItem, NavSignal, StandardInputs
from crm_epic_events.utils.printers import print_error, print_success, print_validation_errors
from crm_epic_events.views import CustomerView, MainMenuView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User


class CustomerController(BaseController):
    """
    Handles navigation and user interactions for customer management.
    Permissions are managed in the controller.
    """

    def __init__(self, db: "Session", user: "User | None"):
        self.db = db
        self.user = user
        self.view = CustomerView()
        self.menu_items = [
            MenuItem(
                "1",
                "List all customers" if self.user.role == Roles.MANAGER else "List my customers",
                self.handle_list,
            ),
            MenuItem("2", "Create a customer", self.handle_create, [*Permissions.CUSTOMER_CREATE]),
            MenuItem("3", "Update a customer", self.handle_update, [*Permissions.CUSTOMER_UPDATE]),
            MenuItem("4", "Delete a customer", self.handle_delete, [*Permissions.CUSTOMER_DELETE]),
            MenuItem(StandardInputs.CANCELLED, "Back to main menu", self.handle_back),
        ]

    def handle_customers_menu(self) -> NavSignal:
        """Runs the customer sub-menu loop,
        dispatching to the selected action until the user navigates back."""
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

    @require_roles(*Permissions.CUSTOMER_CREATE)
    def handle_create(self) -> NavSignal:
        """
        Prompts for customer details and creates a new customer assigned to the current user.

        Raises:
            ValidationError: If the input does not pass Pydantic validation.
            UserNotAllowedError: If the current user's role is not permitted to create a customer.
        """
        raw = self.view.prompt_create()
        try:
            data = CustomerCreateInput(salesperson_id=self.user.id, **raw)
            customer = CustomerService.create(self.user, data, self.db)
            print_success(f"Customer '{customer.first_name} {customer.last_name}' created successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except UserNotAllowedError as error:
            print_error(error.message)
        return NavSignal.STAY

    @require_roles(*Permissions.CUSTOMER_UPDATE)
    def handle_update(self) -> NavSignal:
        """
        Lets the current user select and update one of the eligible customers.

        Managers see all customers; salespersons only see their own.
        Ownership is enforced before the update is applied.

        Raises:
            ValidationError: If the updated input does not pass Pydantic validation.
            UserIsNotOwnerError: If the current user is not the assigned salesperson of the target customer.
        """

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

    @require_roles(*Permissions.CUSTOMER_DELETE)
    def handle_delete(self) -> NavSignal:
        """
        Lets the current user select and delete a customer. Restricted to managers only.

        Raises:
            UserNotAllowedError: If the current user's role is not permitted to delete a customer.
        """
        customers = CustomerService.get_all(self.db)
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
