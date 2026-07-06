import pytest

from crm_epic_events.errors import UserIsNotOwnerError
from crm_epic_events.utils.constants import Roles
from tests.factories import UserFactory

from .fake_controller import FakeController


class TestCheckOwnership:
    """
    check_ownership(owner) raises UserIsNotOwnerError if current user is not
    the owner, except for MANAGER who bypasses the check entirely.
    """

    def test_manager_bypasses_ownership_check(self):
        manager = UserFactory(role=Roles.MANAGER)
        other_user = UserFactory(role=Roles.SALES)
        ctrl = FakeController(manager)
        ctrl.check_ownership(other_user)  # should not raise

    def test_manager_bypasses_when_owner_is_none(self):
        manager = UserFactory(role=Roles.MANAGER)
        ctrl = FakeController(manager)
        ctrl.check_ownership(None)  # should not raise

    def test_sales_owner_can_access_own_resource(self):
        user = UserFactory(role=Roles.SALES)
        ctrl = FakeController(user)
        ctrl.check_ownership(user)  # owner is self.user → should not raise

    def test_support_owner_can_access_own_resource(self):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = FakeController(user)
        ctrl.check_ownership(user)  # owner is self.user → should not raise

    def test_sales_non_owner_cannot_access_resource(self):
        user = UserFactory(role=Roles.SALES)
        other_user = UserFactory(role=Roles.SALES)
        ctrl = FakeController(user)
        with pytest.raises(UserIsNotOwnerError):
            ctrl.check_ownership(other_user)

    def test_support_non_owner_cannot_access_resource(self):
        user = UserFactory(role=Roles.SUPPORT)
        other_user = UserFactory(role=Roles.SUPPORT)
        ctrl = FakeController(user)
        with pytest.raises(UserIsNotOwnerError):
            ctrl.check_ownership(other_user)

    def test_owner_is_none_raises_for_sales(self):
        user = UserFactory(role=Roles.SALES)
        ctrl = FakeController(user)
        with pytest.raises(UserIsNotOwnerError):
            ctrl.check_ownership(None)

    def test_owner_is_none_raises_for_support(self):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = FakeController(user)
        with pytest.raises(UserIsNotOwnerError):
            ctrl.check_ownership(None)
