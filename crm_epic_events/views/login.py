from crm_epic_events.utils import print_error, print_title, prompt, prompt_secret


class LoginView:
    """
    Represents the login view for the epic events crm.
    """

    @staticmethod
    def display() -> str:
        print_title("📖  Epic Events CRM  📖")

        email = prompt("Email")
        password = prompt_secret("Password")

        return email, password

    @staticmethod
    def display_error(message: str) -> None:
        print_error(message)
