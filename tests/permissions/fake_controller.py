from crm_epic_events.controllers.base import BaseController
from crm_epic_events.permissions import Permissions, require_roles


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
    @require_roles(*Permissions.USER_CREATE)
    def user_create(self):
        return self.STATUS_CODE

    @require_roles(*Permissions.USER_UPDATE)
    def user_update(self):
        return self.STATUS_CODE

    @require_roles(*Permissions.USER_DELETE)
    def user_delete(self):
        return self.STATUS_CODE

    # --- Customers ---
    @require_roles(*Permissions.CUSTOMER_CREATE)
    def customer_create(self):
        return self.STATUS_CODE

    @require_roles(*Permissions.CUSTOMER_UPDATE)
    def customer_update(self):
        return self.STATUS_CODE

    @require_roles(*Permissions.CUSTOMER_DELETE)
    def customer_delete(self):
        return self.STATUS_CODE

    # --- Contracts ---
    @require_roles(*Permissions.CONTRACT_CREATE)
    def contract_create(self):
        return self.STATUS_CODE

    @require_roles(*Permissions.CONTRACT_UPDATE)
    def contract_update(self):
        return self.STATUS_CODE

    @require_roles(*Permissions.CONTRACT_DELETE)
    def contract_delete(self):
        return self.STATUS_CODE

    # --- Events ---
    @require_roles(*Permissions.EVENT_CREATE)
    def event_create(self):
        return self.STATUS_CODE

    @require_roles(*Permissions.EVENT_UPDATE)
    def event_update(self):
        return self.STATUS_CODE

    @require_roles(*Permissions.EVENT_DELETE)
    def event_delete(self):
        return self.STATUS_CODE
