from crm_epic_events.utils import print_info, print_title, prompt


class LoginView:
    """
    Represents the login view for the epic events crm.
    """

    @staticmethod
    def display() -> str:
        print_title("📖  Epic Events CRM  📖")

        print_info("Login required")
        email = prompt("Email")
        password = prompt("Password")

        return email, password
