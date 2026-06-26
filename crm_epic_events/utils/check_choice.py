from crm_epic_events.utils import MenuItem
from crm_epic_events.utils.printers import print_error


def check_choice(
    choice: str,
    menu_items: list[MenuItem],
):
    item = next((menu_item for menu_item in menu_items if menu_item.key == choice), None)
    if not item:
        print_error(f"Invalid choice: {choice}")
    return item
