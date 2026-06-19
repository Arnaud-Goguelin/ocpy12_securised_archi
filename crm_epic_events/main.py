from crm_epic_events.controllers import MainController


class Application:

    def __init__(self):

        self.controller = MainController()

    def run(self):

        while True:
            self.controller.handle_main_menu()
