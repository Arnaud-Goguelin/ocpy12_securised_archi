from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.errors import UserNotAllowedError
from crm_epic_events.permissions import require_roles
from crm_epic_events.services import CompanyService
from crm_epic_events.services.company.schemas import CompanyCreateInput, CompanyUpdateInput
from crm_epic_events.utils import check_choice
from crm_epic_events.utils.constants import MenuItem, NavSignal, Roles, StandardInputs
from crm_epic_events.utils.printers import print_error, print_success, print_validation_errors
from crm_epic_events.views import CompanyView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User


class CompanyController(BaseController):
    def __init__(self, db: "Session", user: "User | None"):
        self.db = db
        self.user = user
        self.view = CompanyView()
        self.menu_items = [
            MenuItem("1", "List all companies", self.handle_list),
            MenuItem("2", "Create a company", self.handle_create, [Roles.MANAGER, Roles.SALES]),
            MenuItem("3", "Update a company", self.handle_update, [Roles.MANAGER, Roles.SALES]),
            MenuItem("4", "Delete a company", self.handle_delete, [Roles.MANAGER]),
            MenuItem(StandardInputs.CANCELLED, "Back to main menu", self.handle_back),
        ]

    def handle_companies_menu(self) -> NavSignal:
        while True:
            from crm_epic_events.views.main import MainMenuView  # avoid circular import

            choice = MainMenuView.display(self.visible_menu_items)
            item = check_choice(choice, self.visible_menu_items)
            if item is None:
                continue
            signal = item.action()
            if signal == NavSignal.BACK:
                return NavSignal.BACK

    # --- Handlers ---

    def handle_list(self) -> NavSignal:
        companies = CompanyService.get_all(self.db)
        self.view.display_companies(companies)
        return NavSignal.STAY

    @require_roles(Roles.MANAGER, Roles.SALES)
    def handle_create(self) -> NavSignal:
        raw = self.view.prompt_create()
        try:
            data = CompanyCreateInput(**raw)
            company = CompanyService.create(self.user, data, self.db)
            print_success(f"Company '{company.name}' created successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except (UserNotAllowedError, ValueError) as error:
            print_error(str(error) if isinstance(error, ValueError) else error.message)
        return NavSignal.STAY

    @require_roles(Roles.MANAGER, Roles.SALES)
    def handle_update(self) -> NavSignal:
        companies = CompanyService.get_all(self.db)
        try:
            target = self.view.prompt_select_company(companies)
        except ValueError as error:
            print_error(str(error))
            return NavSignal.STAY

        if target is None:
            return NavSignal.STAY

        raw = self.view.prompt_update(target)
        if not raw:
            print_success("Nothing to update.")
            return NavSignal.STAY

        try:
            data = CompanyUpdateInput(**raw)
            CompanyService.update(self.user, target, data, self.db)
            print_success("Company updated successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        except UserNotAllowedError as error:
            print_error(error.message)
        return NavSignal.STAY

    @require_roles(Roles.MANAGER)
    def handle_delete(self) -> NavSignal:
        companies = CompanyService.get_all(self.db)
        try:
            target = self.view.prompt_select_company(companies)
        except ValueError as error:
            print_error(str(error))
            return NavSignal.STAY

        if target is None:
            return NavSignal.STAY

        try:
            CompanyService.delete(self.user, target, self.db)
            print_success(f"Company '{target.name}' deleted.")
        except UserNotAllowedError as error:
            print_error(error.message)
        return NavSignal.STAY

    @staticmethod
    def handle_back() -> NavSignal:
        return NavSignal.BACK
