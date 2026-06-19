from crm_epic_events.utils import print_title, print_option, prompt, print_error

class MainMenuView:
    """
    Represents the main menu view for the epic events crm.
    """

    MENU_OPTIONS = [
        ("1", "Customers  👥"),
        ("2", "Contracts  📄"),
        ("3", "Events     📅"),
        ("Q", "Quit"),
        ]

    @staticmethod
    def display() -> str:
        print_title("📖  Epic Events CRM  📖")

        for key, label in MainMenuView.MENU_OPTIONS:
            print_option(key, label)

        print()
        return prompt("Choose an option").strip().upper()

    @staticmethod
    def display_invalid_choice(choice: str) -> None:
        print_error(f"Invalid choice: {choice}")
