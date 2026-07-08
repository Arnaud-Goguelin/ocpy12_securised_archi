from enum import Enum

from crm_epic_events.utils import Roles


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
    USER_ASSIGN_ROLE = [Roles.MANAGER]
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

    # --- Company ---
    COMPANY_CREATE = [Roles.MANAGER, Roles.SALES]
    COMPANY_UPDATE = [Roles.MANAGER, Roles.SALES]  # SALES: ownership check needed
    COMPANY_DELETE = [Roles.MANAGER]
