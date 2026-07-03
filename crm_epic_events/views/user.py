from typing import TYPE_CHECKING

from crm_epic_events.utils.constants import Roles
from crm_epic_events.utils.printers import print_info, print_option, print_title, prompt


if TYPE_CHECKING:
    from crm_epic_events.models.user import User


class UserView:
    # --- Prompts ---

    @staticmethod
    def prompt_register() -> dict:
        print_title("Register new user")
        return {
            "first_name": prompt("First name").strip(),
            "last_name": prompt("Last name").strip(),
            "email": prompt("Email").strip(),
            "password": prompt("Password").strip(),
        }

    @staticmethod
    def prompt_update_profile(target_user: "User") -> dict:
        """Prompts only the fields the user wants to change. Empty input = keep current value."""
        print_title(f"Update profile — {target_user.first_name} {target_user.last_name}")
        print_info("Leave blank to keep current value.")
        data = {}
        for field_name, current in [
            ("first_name", target_user.first_name),
            ("last_name", target_user.last_name),
            ("email", target_user.email),
            ("password", None),
        ]:
            label = f"{field_name.replace('_', ' ').title()}"
            if field_name != "password":
                label += f" (current: {current})"
            value = prompt(label).strip()
            if value:
                data[field_name] = value
        return data

    @staticmethod
    def prompt_assign_role(target_user: "User") -> Roles:
        print_title(f"Assign role — {target_user.first_name} {target_user.last_name}")
        print_info(f"Current role: {target_user.role}")
        for i, role in enumerate(Roles, start=1):
            print_option(str(i), role.value.capitalize())
        raw = prompt("Choose a role").strip()
        roles = list(Roles)
        try:
            return roles[int(raw) - 1]
        except (ValueError, IndexError):
            raise ValueError(f"Invalid role choice: '{raw}'") from None

    @staticmethod
    def prompt_select_user(users: list["User"]) -> "User | None":
        """Displays a numbered list and returns the selected User, or None if cancelled."""
        for i, user in enumerate(users, start=1):
            print_option(str(i), f"{user.first_name} {user.last_name}  |  {user.email}  |  {user.role}")
        print_option("Q", "Cancel")
        raw = prompt("Select a user").strip().upper()
        if raw == "Q":
            return None
        try:
            return users[int(raw) - 1]
        except (ValueError, IndexError):
            raise ValueError(f"Invalid selection: '{raw}'") from None

    # --- Display ---

    @staticmethod
    def display_users(users: list["User"], title: str = "Users", display_user_id: bool = False) -> None:
        print_title(title)
        if not users:
            print_info("No users found.")
            return
        for user in users:
            if display_user_id:
                print_info(f"  {user.first_name} {user.last_name}  |  {user.email}  |  {user.role}  |  {user.id}")
            else:
                print_info(f"  {user.first_name} {user.last_name}  |  {user.email}  |  {user.role}")

    @staticmethod
    def display_role_filter_menu() -> Roles | None:
        """Returns the chosen role filter, or None for 'all users'."""
        print_title("Filter users by role")
        print_option("0", "All")
        for i, role in enumerate(Roles, start=1):
            print_option(str(i), role.value.capitalize())
        raw = prompt("Choose a filter").strip()
        if raw == "0":
            return None
        roles = list(Roles)
        try:
            return roles[int(raw) - 1]
        except (ValueError, IndexError):
            raise ValueError(f"Invalid filter: '{raw}'") from None
