from enum import StrEnum


class Roles(StrEnum):
    # in a more commune way, MANAGER = ADMIN, this role is called MANAGER to match with specifications
    MANAGER = "manager"
    SUPPORT = "support"
    SALES = "sales"
