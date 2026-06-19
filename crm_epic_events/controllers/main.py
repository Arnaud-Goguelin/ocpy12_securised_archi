from crm_epic_events.utils import GenericMessages
from crm_epic_events.views import MainMenuView


class MainController:
    """Main controller class to handle the main menu and its actions."""

    def __init__(self):
        self.view = MainMenuView()
        # self.menu_actions = {
        #     "1": self.handle_player_menu,
        #     "2": self.handle_tournament_menu,
        #     CANCELLED_INPUT: self.exit_app,
        # }

    def handle_main_menu(self):
        """
        """
        while True:

            choice = self.view.display()
            # action = self.menu_actions.get(choice)
            # if action:
            #     # action() return True to stay in this menu or False to got back to main menu
            #     should_we_stay_in_this_menu = action()
            #     if not should_we_stay_in_this_menu:
            #         return None
            # else:
            #     # no error raising here to stay in this menu and avoid redirection to main menu
            #     print_invalid_option(
            #         [key for key in self.menu_actions.keys()], False, GenericMessages.MAIN_MENU_RETURN
            #     )

    # def handle_player_menu(self) -> True:
    #     """
    #     Display PlayerController menu screen.
    #     No handle errors here, as it is done in PlayerController.
    #
    #     Returns:
    #         bool: Always returns True. This is designed to ensure continuity of
    #         program operations even in the event of an exception.
    #     """
    #     player_controller = PlayerController(self.data)
    #     player_controller.handle_player_main_menu()
    #     return True
    #
    # def handle_tournament_menu(self) -> True:
    #     """
    #     Display TournamentController menu screen.
    #     No handle errors here, as it is done in TournamentController.
    #
    #     Returns:
    #         bool: Always returns True. This is designed to ensure continuity of
    #         program operations even in the event of an exception.
    #     """
    #     tournament_controller = TournamentController(self.data)
    #     tournament_controller.handle_tournament_main_menu()
    #     return True

    def exit_app(self) -> None:
        """
        Prints an exit message and terminates the application.
        """
        print(GenericMessages.EXIT)
        exit(0)
