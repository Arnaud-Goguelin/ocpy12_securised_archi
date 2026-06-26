from crm_epic_events.utils import MenuItem, StandardInputs, check_choice, exit_app
from crm_epic_events.views import MainMenuView


class MainController:
    """Main controller class to handle the main menu and its actions."""

    def __init__(self):
        self.view = MainMenuView()
        self.menu_items = [
            MenuItem("1", "Manage Customers  👥", self.handle_customers_menu),
            MenuItem("2", "Manage Contracts  📄", self.handle_contracts_menu),
            MenuItem("3", "Manage Events     📅", self.handle_events_menu),
            MenuItem(StandardInputs.CANCELLED, "Quit", self.exit_app),
        ]

    def handle_main_menu(self):
        """ """
        # Todo: first check if user is auth, else display login screen
        while True:
            choice = self.view.display(self.menu_items)
            item = check_choice(choice, self.menu_items)
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

    @staticmethod
    def exit_app() -> None:
        """
        Prints an exit message and terminates the application.
        """
        exit_app()
