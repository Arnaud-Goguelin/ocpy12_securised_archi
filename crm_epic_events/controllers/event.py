from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.errors import (
    ContractNotFoundError,
    ContractNotSignedError,
    UserIsNotOwnerError,
)
from crm_epic_events.permissions import Permissions, Roles, require_roles
from crm_epic_events.services import ContractService, EventService
from crm_epic_events.services.event.schemas import EventCreateInput, EventUpdateInput
from crm_epic_events.utils import check_choice
from crm_epic_events.utils.constants import MenuItem, NavSignal, StandardInputs
from crm_epic_events.utils.printers import print_error, print_success, print_validation_errors
from crm_epic_events.views import EventView, MainMenuView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User


class EventController(BaseController):
    """Handles navigation and user interactions for event management."""

    def __init__(self, db: "Session", user: "User | None"):
        self.db = db
        self.user = user
        self.view = EventView()
        self.menu_items = [
            MenuItem("1", "List all events", self.handle_list),
            MenuItem("2", "List events without support", self.handle_list_without_support),
            MenuItem("3", "Create an event", self.handle_create, [*Permissions.EVENT_CREATE]),
            MenuItem("4", "Update an event", self.handle_update, [*Permissions.EVENT_UPDATE]),
            MenuItem("5", "Delete an event", self.handle_delete, [*Permissions.EVENT_DELETE]),
            MenuItem(StandardInputs.CANCELLED, "Back to main menu", self.handle_back),
        ]

    def handle_events_menu(self) -> NavSignal:
        """Runs the event sub-menu loop, dispatching to the selected action until the user navigates back."""

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
        events = EventService.get_all(self.db)
        self.view.display_events(events, title="All events")
        return NavSignal.STAY

    def handle_list_without_support(self) -> NavSignal:
        events = EventService.get_all_without_support(self.db)
        self.view.display_events(events, title="Events without support")
        return NavSignal.STAY

    @require_roles(*Permissions.EVENT_CREATE)
    def handle_create(self) -> NavSignal:
        """
        Lets a SALES user select one of their signed contracts and create an associated event.

        The customer is automatically inherited from the selected contract.

        Raises:
            ValidationError: If the input does not pass Pydantic validation (e.g. end_date before start_date).
            ContractNotFoundError: If the selected contract no longer exists at creation time.
            ContractNotSignedError: If the selected contract is not signed.
        """

        # Only signed contracts owned by the current salesperson
        all_contracts = ContractService.get_all_by_salesperson(self.user, self.db)
        signed_contracts = [contract for contract in all_contracts if contract.status]

        if not signed_contracts:
            print_error("No signed contracts found for your customers.")
            return NavSignal.STAY

        raw_contract, raw_data = self.view.prompt_create(signed_contracts)
        try:
            contract = signed_contracts[int(raw_contract) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw_contract}'")
            return NavSignal.STAY

        raw_data["contract_id"] = str(contract.id)
        raw_data["customer_id"] = str(contract.customer_id)

        try:
            data = EventCreateInput(**raw_data)
            event = EventService.create(data, self.db)
            print_success(f"Event '{event.id}' created successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except (ContractNotFoundError, ContractNotSignedError) as error:
            print_error(error.message)
        return NavSignal.STAY

    @require_roles(*Permissions.EVENT_UPDATE)
    def handle_update(self) -> NavSignal:
        """
        Lets the current user select and update an event.

        Managers see all events; support users only see events assigned to them.
        Ownership is enforced before the update is applied.

        Raises:
            ValidationError: If the updated input does not pass Pydantic validation.
            UserIsNotOwnerError: If the current user is not the assigned support of the target event.
        """

        # Filter events by support user if not manager, to enforce ownership
        events = (
            EventService.get_all(self.db)
            if self.user.role == Roles.MANAGER
            else EventService.get_all_by_support(self.user, self.db)
        )
        raw = self.view.prompt_select_event(events)
        if raw == StandardInputs.CANCELLED:
            return NavSignal.STAY
        try:
            target = events[int(raw) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw}'")
            return NavSignal.STAY

        self.check_ownership(target.support)

        raw_update = self.view.prompt_update(target)
        if not raw_update:
            print_success("Nothing to update.")
            return NavSignal.STAY

        try:
            data = EventUpdateInput(**raw_update)
            EventService.update(target, data, self.db)
            print_success("Event updated successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except UserIsNotOwnerError as error:
            print_error(error.message)
        return NavSignal.STAY

    @require_roles(*Permissions.EVENT_DELETE)
    def handle_delete(self) -> NavSignal:
        """
        Lets a MANAGER select and delete an event. Restricted to MANAGER only.
        """
        events = EventService.get_all(self.db)
        raw = self.view.prompt_select_event(events)
        if raw == StandardInputs.CANCELLED:
            return NavSignal.STAY
        try:
            target = events[int(raw) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw}'")
            return NavSignal.STAY

        EventService.delete(target, self.db)
        print_success(f"Event '{target.id}' deleted.")
        return NavSignal.STAY

    @staticmethod
    def handle_back() -> NavSignal:
        return NavSignal.BACK
