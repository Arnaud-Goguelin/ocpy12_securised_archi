from typing import TYPE_CHECKING

from pydantic import ValidationError

from crm_epic_events.controllers.base import BaseController
from crm_epic_events.controllers.company import CompanyController
from crm_epic_events.controllers.contract import ContractController
from crm_epic_events.controllers.customer import CustomerController
from crm_epic_events.controllers.user import UserController
from crm_epic_events.models import User
from crm_epic_events.services import UserRegisterInput, UserService
from crm_epic_events.services.authentication.service import AuthService
from crm_epic_events.utils import (
    MenuItem,
    StandardInputs,
    check_choice,
    exit_app,
    print_error,
    print_success,
    print_validation_errors,
)
from crm_epic_events.views import LoginView, MainMenuView, UserView


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class MainController(BaseController):
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
        self.user_view = UserView()
        self.menu_items = [
            MenuItem("1", "Customers", self.handle_customers_menu),
            MenuItem("2", "Contracts", self.handle_contracts_menu),
            MenuItem("3", "Events", self.handle_events_menu),
            MenuItem("4", "Company", self.handle_company_menu),
            MenuItem("5", "Users", self.handle_users_menu),
            MenuItem("6", "Logout", AuthService.logout),
            MenuItem(StandardInputs.CANCELLED, "Quit", self.exit_app),
        ]
        self.guest_menu_items = [
            MenuItem("1", "Login", self.handle_login),
            MenuItem("2", "Create account", self.handle_register),
            MenuItem(StandardInputs.CANCELLED, "Quit", self.exit_app),
        ]

    def handle_main_menu(self):
        while True:
            if not self.user:
                choice = self.main_view.display(self.guest_menu_items)
                item = check_choice(choice, self.guest_menu_items)
                if item is not None:
                    item.action()
                continue

            choice = self.main_view.display(self.visible_menu_items)
            item = check_choice(choice, self.visible_menu_items)
            if item is not None:
                item.action()

    def handle_login(self):
        email, password = self.login_view.display()
        self.user = AuthService.login(email, password, self.db)
        print_success("Login successful!")

    def handle_register(self):
        raw = self.user_view.prompt_register()
        try:
            data = UserRegisterInput(**raw)
            user = UserService.register(data, self.db)
            print_success(f"Account created for '{user.first_name} {user.last_name}'.")
            print_success("A MANAGER will assign your role. You can now log in.")
        except ValidationError as error:
            print_validation_errors(error)
        except ValueError as error:
            print_error(str(error))

    def handle_customers_menu(self):
        controller = CustomerController(self.db, self.user)
        controller.handle_customers_menu()

    def handle_company_menu(self):
        controller = CompanyController(self.db, self.user)
        controller.handle_companies_menu()

    def handle_contracts_menu(self):
        controller = ContractController(self.db, self.user)
        controller.handle_contracts_menu()

    def handle_events_menu(self):
        pass

    def handle_users_menu(self):
        controller = UserController(self.db, self.user)
        controller.handle_users_menu()

    @staticmethod
    def exit_app() -> None:
        """
        Prints an exit message and terminates the application.
        """
        exit_app()
