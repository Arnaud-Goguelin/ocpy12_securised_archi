from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, StrEnum, auto


class Roles(StrEnum):
    # in a more commune way, MANAGER = ADMIN, this role is called MANAGER to match with specifications
    MANAGER = "manager"
    SUPPORT = "support"
    SALES = "sales"


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
