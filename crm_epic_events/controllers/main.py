from typing import TYPE_CHECKING

from crm_epic_events.models import User
from crm_epic_events.services.authentication.service import AuthService
from crm_epic_events.utils import MenuItem, Roles, StandardInputs, check_choice, exit_app, print_success
from crm_epic_events.views import LoginView, MainMenuView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class MainController:
    """Main controller class to handle the main menu and its actions."""

    def __init__(
        self,
        db: "Session",
        user: "User | None",
    ):
        self.db = db
        self.user = user
        self.main_view = MainMenuView()
        self.login_view = LoginView()
        self.main_menu_items = [
            MenuItem("1", "Customers", self.handle_customers_menu),
            MenuItem("2", "Contracts", self.handle_contracts_menu),
            MenuItem("3", "Events", self.handle_events_menu),
            MenuItem("4", "Users", self.handle_users_menu, [Roles.MANAGER]),
            MenuItem(StandardInputs.CANCELLED, "Quit", self.exit_app),
        ]

    @property
    def visible_menu_items(self):
        return [item for item in self.main_menu_items if self.user.role in item.roles_allowed]

    def handle_main_menu(self):
        """ """
        while True:
            if not self.user:
                email, password = self.login_view.display()
                self.user = AuthService.login(email, password, self.db)
                print_success("Login successful!")
                continue

            choice = self.main_view.display(self.visible_menu_items)
            item = check_choice(choice, self.visible_menu_items)
            if item is None:
                continue
            else:
                item.action()

    def handle_customers_menu(self):
        pass

    def handle_contracts_menu(self):
        pass

    def handle_events_menu(self):
        pass

    def handle_users_menu(self):
        pass

    @staticmethod
    def exit_app() -> None:
        """
        Prints an exit message and terminates the application.
        """
        exit_app()
