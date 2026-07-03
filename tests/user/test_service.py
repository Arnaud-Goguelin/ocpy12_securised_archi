# tests/services/user/test_service.py
from unittest.mock import patch

import bcrypt
import pytest

from crm_epic_events.models import User
from crm_epic_events.services.user.schemas import UserAssignRoleInput, UserRegisterInput, UserUpdateInput
from crm_epic_events.services.user.service import UserService
from crm_epic_events.utils import Roles
from tests.factories import UserFactory


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_get_all_returns_users(self, mock_db):
        users = UserFactory.build_batch(3)
        with patch.object(User, "get_all", return_value=users):
            result = UserService.get_all(mock_db)

        assert result == users

    def test_get_all_returns_empty_list(self, mock_db):
        with patch.object(User, "get_all", return_value=[]):
            result = UserService.get_all(mock_db)

        assert result == []


# ── get_all_by_role ───────────────────────────────────────────────────────────


class TestGetAllByRole:
    def test_get_all_by_role_returns_filtered_users(self, mock_db):
        managers = UserFactory.build_batch(2, role=Roles.MANAGER)
        with patch.object(User, "get_all_by_role", return_value=managers):
            result = UserService.get_all_by_role(Roles.MANAGER, mock_db)

        assert result == managers

    def test_get_all_by_role_returns_empty_list(self, mock_db):
        with patch.object(User, "get_all_by_role", return_value=[]):
            result = UserService.get_all_by_role(Roles.SALES, mock_db)

        assert result == []


# ── register ──────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_success(self, mock_db):
        data = UserRegisterInput(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="securepassword",
        )
        created_user = UserFactory()

        with (
            patch.object(User, "get_by_email", return_value=None),
            patch.object(User, "create", return_value=created_user),
        ):
            result = UserService.register(data, mock_db)

        assert result == created_user

    def test_register_hashes_password(self, mock_db):
        data = UserRegisterInput(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            password="securepassword",
        )
        created_user = UserFactory()

        with (
            patch.object(User, "get_by_email", return_value=None),
            patch.object(User, "create", return_value=created_user) as mock_create,
        ):
            UserService.register(data, mock_db)

        _, _, _, hashed, _ = mock_create.call_args.args
        assert bcrypt.checkpw(b"securepassword", hashed.encode())

    def test_register_raises_if_email_already_in_use(self, mock_db, user):
        data = UserRegisterInput(
            first_name="John",
            last_name="Doe",
            email=user.email,
            password="securepassword",
        )

        with (
            patch.object(User, "get_by_email", return_value=user),
            pytest.raises(ValueError, match="already in use"),
        ):
            UserService.register(data, mock_db)

    def test_register_password_too_short_raises(self):
        with pytest.raises(ValueError, match="at least 8 characters"):
            UserRegisterInput(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                password="short",
            )


# ── update_profile ────────────────────────────────────────────────────────────


class TestUpdateProfile:
    def test_manager_can_update_any_user(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = UserFactory(role=Roles.SALES)
        data = UserUpdateInput(first_name="Updated")
        updated_user = UserFactory(role=Roles.SALES, first_name="Updated")

        with patch.object(User, "update", return_value=updated_user):
            result = UserService.update_profile(manager, target, data, mock_db)

        assert result == updated_user

    def test_non_manager_cannot_change_role(self, mock_db):
        sales_user = UserFactory(role=Roles.SALES)
        data = UserUpdateInput(role=Roles.MANAGER)
        updated_user = UserFactory(role=Roles.SALES)

        with patch.object(User, "update", return_value=updated_user) as mock_update:
            UserService.update_profile(sales_user, sales_user, data, mock_db)

        # patch.object on an instance method: self is NOT in args, args[0] is data
        passed_data: UserUpdateInput = mock_update.call_args.args[0]
        assert passed_data.role is None

    def test_manager_can_update_target_not_self(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = UserFactory(role=Roles.SALES)
        data = UserUpdateInput(first_name="Updated")
        updated_user = UserFactory(role=Roles.SALES, first_name="Updated")

        # Patch update on each instance separately to know which one was called
        from unittest.mock import MagicMock

        manager.update = MagicMock(return_value=updated_user)
        target.update = MagicMock(return_value=updated_user)

        UserService.update_profile(manager, target, data, mock_db)

        target.update.assert_called_once()
        manager.update.assert_not_called()

    def test_manager_can_change_role(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = UserFactory(role=Roles.SALES)
        data = UserUpdateInput(role=Roles.SUPPORT)
        updated_user = UserFactory(role=Roles.SUPPORT)

        with patch.object(User, "update", return_value=updated_user) as mock_update:
            UserService.update_profile(manager, target, data, mock_db)

        # patch.object on an instance method: args[0] is data
        passed_data: UserUpdateInput = mock_update.call_args.args[0]
        assert passed_data.role == Roles.SUPPORT

    def test_password_is_hashed_on_update(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        data = UserUpdateInput(password="newpassword123")

        with patch.object(User, "update", return_value=user) as mock_update:
            UserService.update_profile(user, user, data, mock_db)

        # patch.object on an instance method: args[0] is data
        passed_data: UserUpdateInput = mock_update.call_args.args[0]
        assert bcrypt.checkpw(b"newpassword123", passed_data.password.encode())

    def test_update_password_too_short_raises(self):
        with pytest.raises(ValueError, match="at least 8 characters"):
            UserUpdateInput(password="short")


# ── assign_role ───────────────────────────────────────────────────────────────


class TestAssignRole:
    def test_assign_role_success(self, mock_db):
        target = UserFactory(role=Roles.SALES)
        data = UserAssignRoleInput(role=Roles.SUPPORT)
        updated_user = UserFactory(role=Roles.SUPPORT)

        with patch.object(User, "update", return_value=updated_user):
            result = UserService.assign_role(target, data, mock_db)

        assert result == updated_user

    def test_assign_role_calls_update_with_correct_data(self, mock_db):
        target = UserFactory(role=Roles.SALES)
        data = UserAssignRoleInput(role=Roles.MANAGER)

        # Patch on the instance directly to verify it's called on target
        from unittest.mock import MagicMock

        target.update = MagicMock(return_value=target)

        UserService.assign_role(target, data, mock_db)

        target.update.assert_called_once_with(data, mock_db)


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_delete_calls_delete_on_target(self, mock_db):
        target = UserFactory()

        from unittest.mock import MagicMock

        target.delete = MagicMock(return_value=None)

        UserService.delete(target, mock_db)

        target.delete.assert_called_once_with(mock_db)

    def test_delete_returns_none(self, mock_db):
        target = UserFactory()

        with patch.object(User, "delete", return_value=None):
            result = UserService.delete(target, mock_db)

        assert result is None
