from crm_epic_events.utils import print_title, prompt


class LoginView:
    """
    Represents the login view for the epic events crm.
    """

    @staticmethod
    def display() -> str:
        print_title("📖  Epic Events CRM  📖")

        email = prompt("Email")
        password = prompt("Password")

        return email, password
