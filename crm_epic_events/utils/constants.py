from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, StrEnum, auto


class Roles(StrEnum):
    # in a more commune way, MANAGER = ADMIN, this role is called MANAGER to match with specifications
    MANAGER = "manager"
    SUPPORT = "support"
    SALES = "sales"


class Permissions(list[Roles], Enum):
    """
    Defines the Permissions class to manage roles access control for various
    system actions.

    Here is the architecture logic:
    Member: action on an object = Value: list of roles allowed to perform the action

    Ownership checks is NOT included in the permissions.
    """

    # Reminder from specifications: all roles can read all objects

    # --- Users ---
    USER_CREATE = [Roles.MANAGER]
    USER_UPDATE = [Roles.MANAGER]
    USER_DELETE = [Roles.MANAGER]

    # --- Customers ---
    CUSTOMER_CREATE = [Roles.SALES]
    CUSTOMER_UPDATE = [Roles.MANAGER, Roles.SALES]  # SALES: ownership check needed
    CUSTOMER_DELETE = [Roles.MANAGER]

    # --- Contracts ---
    CONTRACT_CREATE = [Roles.MANAGER]
    CONTRACT_UPDATE = [Roles.MANAGER, Roles.SALES]  # SALES: ownership check needed
    CONTRACT_DELETE = [Roles.MANAGER]

    # --- Events ---
    EVENT_CREATE = [Roles.SALES]  # SALES: ownership check needed
    EVENT_UPDATE = [Roles.MANAGER, Roles.SUPPORT]  # SUPPORT: ownership check needed
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
    """
    Represents a menu item for a user interface.

    This class is used to define a single item in a menu, associating it with a
    unique key, display label, an action to perform when selected, and optional
    permissions to restrict its visibility to certain roles.
    """

    key: str
    label: str
    action: Callable
    # default: all Roles are allowed
    roles_allowed: list[Roles] = field(default_factory=lambda: [*Roles])
