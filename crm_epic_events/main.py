from crm_epic_events.controllers import MainController
from crm_epic_events.utils import GenericMessages, print_unexpected_error


class Application:
    def __init__(self):

        self.controller = MainController()

    def run(self):
        try:
            self.controller.handle_main_menu()
        except Exception as error:
            print_unexpected_error(str(error), GenericMessages.MAIN_MENU_RETURN)
            self.controller.handle_main_menu()
