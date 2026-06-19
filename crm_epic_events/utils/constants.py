from enum import StrEnum


class Roles(StrEnum):
    # in a more commune way, MANAGER = ADMIN, this role is called MANAGER to match with specifications
    MANAGER = "manager"
    SUPPORT = "support"
    SALES = "sales"


class GenericMessages(StrEnum):
    INVALID_INPUT = "Invalid input. Please try again."
    INVALID_CHOICE = "Invalid choice. Please try again."
    EXIT = "Exiting the program."
