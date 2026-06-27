from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, StrEnum, auto


class Roles(StrEnum):
    # in a more commune way, MANAGER = ADMIN, this role is called MANAGER to match with specifications
    MANAGER = "manager"
    SUPPORT = "support"
    SALES = "sales"


class Permissions(list[Roles], Enum):
    # Reminder from specifications: all roles can read all objects

    # --- Users ---
    USER_CREATE = [Roles.MANAGER]
    USER_UPDATE = [Roles.MANAGER]
    USER_DELETE = [Roles.MANAGER]

    # --- Customers ---
    CUSTOMER_CREATE = [Roles.SALES]
    CUSTOMER_UPDATE = [Roles.MANAGER, Roles.SALES]  # SALES: only their own customers (ownership check)
    CUSTOMER_DELETE = [Roles.MANAGER]

    # --- Contracts ---
    CONTRACT_CREATE = [Roles.MANAGER]
    CONTRACT_UPDATE = [Roles.MANAGER, Roles.SALES]  # SALES: only contracts of their own customers (ownership check)
    CONTRACT_DELETE = [Roles.MANAGER]

    # --- Events ---
    EVENT_CREATE = [Roles.SALES]  # SALES: only for their customers with a signed contract (ownership check)
    EVENT_UPDATE = [Roles.MANAGER, Roles.SUPPORT]  # SUPPORT: only their own events (ownership check)
    EVENT_DELETE = [Roles.MANAGER]


class GenericMessages(StrEnum):
    EXIT = "Exiting the program."
    MAIN_MENU_RETURN = "Go back to Main menu in ... "


class StandardInputs(StrEnum):
    CANCELLED = "Q"
    NEGATION = "N"
    VALIDATION = "Y"


class NavSignal(Enum):
    STAY = auto()
    BACK = auto()
    EXIT = auto()


@dataclass
class MenuItem:
    key: str
    label: str
    action: Callable
