from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.errors import (
    ContractNotFoundError,
    ContractNotSignedError,
    UserIsNotOwnerError,
)
from crm_epic_events.permissions import require_roles
from crm_epic_events.services import ContractService, EventService
from crm_epic_events.services.event.schemas import EventCreateInput, EventUpdateInput
from crm_epic_events.utils import check_choice
from crm_epic_events.utils.constants import MenuItem, NavSignal, Roles, StandardInputs
from crm_epic_events.utils.printers import print_error, print_success, print_validation_errors
from crm_epic_events.views import EventView, MainMenuView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User


class EventController(BaseController):
    def __init__(self, db: "Session", user: "User | None"):
        self.db = db
        self.user = user
        self.view = EventView()
        self.menu_items = [
            MenuItem("1", "List my events" if self.user.role == Roles.SUPPORT else "List all events", self.handle_list),
            MenuItem("2", "List events without support", self.handle_list_without_support, [Roles.MANAGER]),
            MenuItem("3", "Create an event", self.handle_create, [Roles.SALES]),
            MenuItem("4", "Update an event", self.handle_update, [Roles.MANAGER, Roles.SUPPORT]),
            MenuItem("5", "Delete an event", self.handle_delete, [Roles.MANAGER]),
            MenuItem(StandardInputs.CANCELLED, "Back to main menu", self.handle_back),
        ]

    def handle_events_menu(self) -> NavSignal:
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

    @require_roles(Roles.MANAGER)
    def handle_list_without_support(self) -> NavSignal:
        events = EventService.get_all_without_support(self.db)
        self.view.display_events(events, title="Events without support")
        return NavSignal.STAY

    @require_roles(Roles.SALES)
    def handle_create(self) -> NavSignal:
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

    @require_roles(Roles.MANAGER, Roles.SUPPORT)
    def handle_update(self) -> NavSignal:
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

    @require_roles(Roles.MANAGER)
    def handle_delete(self) -> NavSignal:
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
