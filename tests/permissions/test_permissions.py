import pytest

from crm_epic_events.errors import UserNotAllowedError
from crm_epic_events.utils.constants import Roles
from tests.factories import UserFactory

from .fake_controller import FakeController


# ════════════════════════════════════════════════════════════════════════════
# @require_roles — unauthenticated
# ════════════════════════════════════════════════════════════════════════════


class TestUnauthenticated:
    """No user should be able to access any protected action."""

    def test_unauthenticated_cannot_access_any_action(self):
        ctrl = FakeController(user=None)
        for action in [
            ctrl.user_create,
            ctrl.user_update,
            ctrl.user_delete,
            ctrl.customer_create,
            ctrl.customer_update,
            ctrl.customer_delete,
            ctrl.contract_create,
            ctrl.contract_update,
            ctrl.contract_delete,
            ctrl.event_create,
            ctrl.event_update,
            ctrl.event_delete,
        ]:
            with pytest.raises(UserNotAllowedError):
                action()


# ════════════════════════════════════════════════════════════════════════════
# @require_roles — Users
# ════════════════════════════════════════════════════════════════════════════


class TestUserPermissions:
    def test_manager_can_create_user(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).user_create() == FakeController.STATUS_CODE

    def test_sales_cannot_create_user(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SALES)).user_create()

    def test_support_cannot_create_user(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).user_create()

    def test_manager_can_update_user(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).user_update() == FakeController.STATUS_CODE

    def test_sales_cannot_update_user(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SALES)).user_update()

    def test_support_cannot_update_user(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).user_update()

    def test_manager_can_delete_user(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).user_delete() == FakeController.STATUS_CODE

    def test_sales_cannot_delete_user(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SALES)).user_delete()

    def test_support_cannot_delete_user(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).user_delete()


# ════════════════════════════════════════════════════════════════════════════
# @require_roles — Customers
# ════════════════════════════════════════════════════════════════════════════


class TestCustomerPermissions:
    def test_sales_can_create_customer(self):
        assert FakeController(UserFactory(role=Roles.SALES)).customer_create() == FakeController.STATUS_CODE

    def test_manager_cannot_create_customer(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.MANAGER)).customer_create()

    def test_support_cannot_create_customer(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).customer_create()

    def test_manager_can_update_customer(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).customer_update() == FakeController.STATUS_CODE

    def test_sales_can_update_customer(self):
        assert FakeController(UserFactory(role=Roles.SALES)).customer_update() == FakeController.STATUS_CODE

    def test_support_cannot_update_customer(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).customer_update()

    def test_manager_can_delete_customer(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).customer_delete() == FakeController.STATUS_CODE

    def test_sales_cannot_delete_customer(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SALES)).customer_delete()

    def test_support_cannot_delete_customer(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).customer_delete()


# ════════════════════════════════════════════════════════════════════════════
# @require_roles — Contracts
# ════════════════════════════════════════════════════════════════════════════


class TestContractPermissions:
    def test_manager_can_create_contract(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).contract_create() == FakeController.STATUS_CODE

    def test_sales_cannot_create_contract(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SALES)).contract_create()

    def test_support_cannot_create_contract(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).contract_create()

    def test_manager_can_update_contract(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).contract_update() == FakeController.STATUS_CODE

    def test_sales_can_update_contract(self):
        assert FakeController(UserFactory(role=Roles.SALES)).contract_update() == FakeController.STATUS_CODE

    def test_support_cannot_update_contract(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).contract_update()

    def test_manager_can_delete_contract(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).contract_delete() == FakeController.STATUS_CODE

    def test_sales_cannot_delete_contract(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SALES)).contract_delete()

    def test_support_cannot_delete_contract(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).contract_delete()


# ════════════════════════════════════════════════════════════════════════════
# @require_roles — Events
# ════════════════════════════════════════════════════════════════════════════


class TestEventPermissions:
    def test_sales_can_create_event(self):
        assert FakeController(UserFactory(role=Roles.SALES)).event_create() == FakeController.STATUS_CODE

    def test_manager_cannot_create_event(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.MANAGER)).event_create()

    def test_support_cannot_create_event(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).event_create()

    def test_manager_can_update_event(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).event_update() == FakeController.STATUS_CODE

    def test_support_can_update_event(self):
        assert FakeController(UserFactory(role=Roles.SUPPORT)).event_update() == FakeController.STATUS_CODE

    def test_sales_cannot_update_event(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SALES)).event_update()

    def test_manager_can_delete_event(self):
        assert FakeController(UserFactory(role=Roles.MANAGER)).event_delete() == FakeController.STATUS_CODE

    def test_sales_cannot_delete_event(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SALES)).event_delete()

    def test_support_cannot_delete_event(self):
        with pytest.raises(UserNotAllowedError):
            FakeController(UserFactory(role=Roles.SUPPORT)).event_delete()
