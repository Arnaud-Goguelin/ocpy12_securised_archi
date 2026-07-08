from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.permissions import Permissions, Roles, require_roles
from crm_epic_events.services import UserAssignRoleInput, UserService, UserUpdateInput
from crm_epic_events.utils import check_choice
from crm_epic_events.utils.constants import MenuItem, NavSignal, StandardInputs
from crm_epic_events.utils.printers import print_error, print_success, print_validation_errors
from crm_epic_events.views import UserView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models.user import User


class UserController(BaseController):
    def __init__(self, db: "Session", user: "User | None"):
        self.db = db
        self.user = user
        self.view = UserView()
        self.menu_items = [
            MenuItem("1", "List users", self.handle_list),
            MenuItem("2", "Update my profile", self.handle_update_profile_self),
            MenuItem("3", "Update a user", self.handle_update_profile_other, [*Permissions.USER_UPDATE]),
            MenuItem("4", "Assign role", self.handle_assign_role, [*Permissions.USER_ASSIGN_ROLE]),
            MenuItem("5", "Delete a user", self.handle_delete, [*Permissions.USER_DELETE]),
            MenuItem(StandardInputs.CANCELLED, "Back to main menu", self.handle_back),
        ]

    def handle_users_menu(self) -> NavSignal:
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
        raw = self.view.display_role_filter_menu()
        if raw == "0":
            users = UserService.get_all(self.db)
            title = "All users"
        else:
            roles = list(Roles)
            try:
                role_filter = roles[int(raw) - 1]
            except (ValueError, IndexError):
                print_error(f"Invalid filter: '{raw}'")
                return NavSignal.STAY
            users = UserService.get_all_by_role(role_filter, self.db)
            title = f"Users — {role_filter.value.capitalize()}"

        display_user_id = self.user.role == Roles.MANAGER
        self.view.display_users(users, title, display_user_id)
        return NavSignal.STAY

    def handle_update_profile_self(self) -> NavSignal:

        raw = self.view.prompt_update_profile(self.user)
        if not raw:
            print_success("Nothing to update.")
            return NavSignal.STAY

        try:
            data = UserUpdateInput(**raw)
            UserService.update_profile(self.user, self.user, data, self.db)
            print_success("Profile updated successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        return NavSignal.STAY

    @require_roles(*Permissions.USER_UPDATE)
    def handle_update_profile_other(self) -> NavSignal:
        users = UserService.get_all(self.db)
        users.remove(self.user)
        raw = self.view.prompt_select_user(users)
        if raw == StandardInputs.CANCELLED:
            return NavSignal.STAY
        try:
            target = users[int(raw) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw}'")
            return NavSignal.STAY

        if target is None:
            return NavSignal.STAY
        raw = self.view.prompt_update_profile(target)
        if not raw:
            print_success("Nothing to update.")
            return NavSignal.STAY

        try:
            data = UserUpdateInput(**raw)
            UserService.update_profile(self.user, target, data, self.db)
            print_success("User updated successfully.")
        except ValidationError as error:
            print_validation_errors(error)
        return NavSignal.STAY

    @require_roles(*Permissions.USER_ASSIGN_ROLE)
    def handle_assign_role(self) -> NavSignal:
        users = UserService.get_all(self.db)
        raw = self.view.prompt_select_user(users)
        if raw == StandardInputs.CANCELLED:
            return NavSignal.STAY
        try:
            target = users[int(raw) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw}'")
            return NavSignal.STAY

        raw_role = self.view.prompt_assign_role(target)
        roles = list(Roles)
        try:
            role = roles[int(raw_role) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid role choice: '{raw_role}'")
            return NavSignal.STAY

        try:
            data = UserAssignRoleInput(role=role)
            UserService.assign_role(target, data, self.db)
            print_success(f"Role '{role}' assigned to {target.first_name} {target.last_name}.")
        except ValidationError as error:
            print_validation_errors(error)
        return NavSignal.STAY

    @require_roles(*Permissions.USER_DELETE)
    def handle_delete(self) -> NavSignal:
        users = UserService.get_all(self.db)
        users.remove(self.user)
        raw = self.view.prompt_select_user(users)
        if raw == StandardInputs.CANCELLED:
            return NavSignal.STAY
        try:
            target = users[int(raw) - 1]
        except (ValueError, IndexError):
            print_error(f"Invalid selection: '{raw}'")
            return NavSignal.STAY

        if target is None:
            return NavSignal.STAY

        try:
            UserService.delete(target, self.db)
            print_success(f"User '{target.first_name} {target.last_name}' deleted.")
        except ValueError as error:
            print_error(str(error))
        return NavSignal.STAY

    @staticmethod
    def handle_back() -> NavSignal:
        return NavSignal.BACK
