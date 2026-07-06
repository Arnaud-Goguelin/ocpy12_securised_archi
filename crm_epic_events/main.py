import traceback

from crm_epic_events.config import Config
from crm_epic_events.controllers import MainController
from crm_epic_events.models.database import get_db

# from crm_epic_events.models.start_tasks import setup_database
from crm_epic_events.services.authentication.service import AuthService
from crm_epic_events.utils import GenericMessages, print_info, print_unexpected_error


class Application:
    def __init__(self):
        self.db = get_db()
        self.user = AuthService.get_current_user(self.db)
        self.controller = MainController(self.db, self.user)

    def run(self):
        # setup_database()
        try:
            while True:
                try:
                    self.controller.handle_main_menu()
                    break
                except Exception as error:
                    print_unexpected_error(str(error), GenericMessages.MAIN_MENU_RETURN)
                    if Config.APP_ENV == "local":
                        print_info(traceback.format_exc())
                    # do not recall self.controller.handle_main_menu()
                    # but let while true loop continue
                    # because if handle_main_menu re raise an error,
                    # to recall it would not let a recursion error raise
                    continue
        finally:
            # close DB only when app exits
            # otherwise, session would be closed before handle_main_menu returns or raises an error
            self.db.close()
