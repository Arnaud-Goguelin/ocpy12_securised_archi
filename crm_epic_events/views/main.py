from crm_epic_events.utils import MenuItem, print_option, print_title, prompt


class MainMenuView:
    """
    Represents the main menu view for the epic events crm.
    """

    @staticmethod
    def display(menu_items: list[MenuItem]) -> str:
        print_title("📖  Epic Events CRM  📖")
        for item in menu_items:
            print_option(item.key, item.label)
        print()
        return prompt("Choose an option").strip().upper()
