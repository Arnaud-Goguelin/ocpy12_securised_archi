from crm_epic_events.controllers.base import BaseController
from crm_epic_events.permissions import require_roles
from crm_epic_events.utils.constants import Roles


class FakeController(BaseController):
    """
    Minimal controller stub — mirrors the real permission matrix from constants.py.
    Each method maps to one Permissions entry.
    """

    STATUS_CODE = 200

    def __init__(self, user):
        self.user = user
        self.menu_items = []

    # --- Users ---
    @require_roles(Roles.MANAGER)
    def user_create(self):
        return self.STATUS_CODE

    @require_roles(Roles.MANAGER)
    def user_update(self):
        return self.STATUS_CODE

    @require_roles(Roles.MANAGER)
    def user_delete(self):
        return self.STATUS_CODE

    # --- Customers ---
    @require_roles(Roles.SALES)
    def customer_create(self):
        return self.STATUS_CODE

    @require_roles(Roles.MANAGER, Roles.SALES)
    def customer_update(self):
        return self.STATUS_CODE

    @require_roles(Roles.MANAGER)
    def customer_delete(self):
        return self.STATUS_CODE

    # --- Contracts ---
    @require_roles(Roles.MANAGER)
    def contract_create(self):
        return self.STATUS_CODE

    @require_roles(Roles.MANAGER, Roles.SALES)
    def contract_update(self):
        return self.STATUS_CODE

    @require_roles(Roles.MANAGER)
    def contract_delete(self):
        return self.STATUS_CODE

    # --- Events ---
    @require_roles(Roles.SALES)
    def event_create(self):
        return self.STATUS_CODE

    @require_roles(Roles.MANAGER, Roles.SUPPORT)
    def event_update(self):
        return self.STATUS_CODE

    @require_roles(Roles.MANAGER)
    def event_delete(self):
        return self.STATUS_CODE
