from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, StrEnum, auto

from crm_epic_events.permissions import Roles


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
    roles_allowed: list["Roles"] = field(default_factory=lambda: [*Roles])
