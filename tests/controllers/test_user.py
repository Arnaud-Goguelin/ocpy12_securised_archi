from unittest.mock import MagicMock, patch

import pytest

from crm_epic_events.controllers.user import UserController
from crm_epic_events.errors import UserNotAllowedError
from crm_epic_events.services.user.service import UserService
from crm_epic_events.utils.constants import NavSignal, Roles, StandardInputs
from tests.factories import UserFactory


# ── handle_list ───────────────────────────────────────────────────────────────


class TestHandleList:
    def test_any_role_can_list(self, mock_db):
        for role in Roles:
            user = UserFactory(role=role)
            ctrl = UserController(mock_db, user)
            ctrl.view.display_role_filter_menu = MagicMock(return_value="0")
            with patch.object(UserService, "get_all", return_value=[]):
                signal = ctrl.handle_list()
            assert signal == NavSignal.STAY

    def test_filter_by_role_calls_get_all_by_role(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = UserController(mock_db, user)
        ctrl.view.display_role_filter_menu = MagicMock(return_value="1")  # first role = MANAGER

        with patch.object(UserService, "get_all_by_role", return_value=[]) as mock_get:
            ctrl.handle_list()

        mock_get.assert_called_once()

    def test_invalid_filter_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.MANAGER)
        ctrl = UserController(mock_db, user)
        ctrl.view.display_role_filter_menu = MagicMock(return_value="invalid")

        signal = ctrl.handle_list()

        assert signal == NavSignal.STAY


# ── handle_update_profile_self ────────────────────────────────────────────────


class TestHandleUpdateProfileSelf:
    def test_any_role_can_update_own_profile(self, mock_db):
        for role in Roles:
            user = UserFactory(role=role)
            ctrl = UserController(mock_db, user)
            ctrl.view.prompt_update_profile = MagicMock(return_value={"first_name": "New"})

            with patch.object(UserService, "update_profile", return_value=user):
                signal = ctrl.handle_update_profile_self()

            assert signal == NavSignal.STAY

    def test_nothing_to_update_returns_stay(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, user)
        ctrl.view.prompt_update_profile = MagicMock(return_value={})

        signal = ctrl.handle_update_profile_self()

        assert signal == NavSignal.STAY


# ── handle_update_profile_other ───────────────────────────────────────────────


class TestHandleUpdateProfileOther:
    def test_manager_can_update_other_user(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        other_user = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, manager)
        ctrl.view.prompt_select_user = MagicMock(return_value="1")
        ctrl.view.prompt_update_profile = MagicMock(return_value={"first_name": "Updated"})

        with (
            patch.object(UserService, "get_all", return_value=[other_user, manager]),
            patch.object(UserService, "update_profile", return_value=other_user),
        ):
            signal = ctrl.handle_update_profile_other()

        assert signal == NavSignal.STAY

    def test_sales_cannot_update_other_user(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_update_profile_other()

    def test_support_cannot_update_other_user(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = UserController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_update_profile_other()

    def test_cancelled_returns_stay(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        ctrl = UserController(mock_db, manager)
        ctrl.view.prompt_select_user = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(UserService, "get_all", return_value=[manager]):
            signal = ctrl.handle_update_profile_other()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        ctrl = UserController(mock_db, manager)
        users = UserFactory.build_batch(2)
        ctrl.view.prompt_select_user = MagicMock(return_value="invalid")

        with patch.object(UserService, "get_all", return_value=[*users, manager]):
            signal = ctrl.handle_update_profile_other()

        assert signal == NavSignal.STAY

    def test_nothing_to_update_returns_stay(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        other_user = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, manager)
        ctrl.view.prompt_select_user = MagicMock(return_value="1")
        ctrl.view.prompt_update_profile = MagicMock(return_value={})

        with patch.object(UserService, "get_all", return_value=[other_user, manager]):
            signal = ctrl.handle_update_profile_other()

        assert signal == NavSignal.STAY


# ── handle_assign_role ────────────────────────────────────────────────────────


class TestHandleAssignRole:
    def test_manager_can_assign_role(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, manager)
        ctrl.view.prompt_select_user = MagicMock(return_value="1")
        ctrl.view.prompt_assign_role = MagicMock(return_value="1")  # first role

        with (
            patch.object(UserService, "get_all", return_value=[target]),
            patch.object(UserService, "assign_role", return_value=target),
        ):
            signal = ctrl.handle_assign_role()

        assert signal == NavSignal.STAY

    def test_sales_cannot_assign_role(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_assign_role()

    def test_support_cannot_assign_role(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = UserController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_assign_role()

    def test_cancelled_returns_stay(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        ctrl = UserController(mock_db, manager)
        ctrl.view.prompt_select_user = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(UserService, "get_all", return_value=[]):
            signal = ctrl.handle_assign_role()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        ctrl = UserController(mock_db, manager)
        users = UserFactory.build_batch(2)
        ctrl.view.prompt_select_user = MagicMock(return_value="invalid")

        with patch.object(UserService, "get_all", return_value=users):
            signal = ctrl.handle_assign_role()

        assert signal == NavSignal.STAY

    def test_invalid_role_choice_returns_stay(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, manager)
        ctrl.view.prompt_select_user = MagicMock(return_value="1")
        ctrl.view.prompt_assign_role = MagicMock(return_value="invalid")

        with patch.object(UserService, "get_all", return_value=[target]):
            signal = ctrl.handle_assign_role()

        assert signal == NavSignal.STAY


# ── handle_delete ─────────────────────────────────────────────────────────────


class TestHandleDelete:
    def test_manager_can_delete(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        target = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, manager)
        ctrl.view.prompt_select_user = MagicMock(return_value="1")

        with (
            patch.object(UserService, "get_all", return_value=[target, manager]),
            patch.object(UserService, "delete") as mock_delete,
        ):
            signal = ctrl.handle_delete()

        mock_delete.assert_called_once_with(target, mock_db)
        assert signal == NavSignal.STAY

    def test_sales_cannot_delete(self, mock_db):
        user = UserFactory(role=Roles.SALES)
        ctrl = UserController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_delete()

    def test_support_cannot_delete(self, mock_db):
        user = UserFactory(role=Roles.SUPPORT)
        ctrl = UserController(mock_db, user)
        with pytest.raises(UserNotAllowedError):
            ctrl.handle_delete()

    def test_cancelled_returns_stay(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        ctrl = UserController(mock_db, manager)
        ctrl.view.prompt_select_user = MagicMock(return_value=StandardInputs.CANCELLED)

        with patch.object(UserService, "get_all", return_value=[manager]):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY

    def test_invalid_selection_returns_stay(self, mock_db):
        manager = UserFactory(role=Roles.MANAGER)
        ctrl = UserController(mock_db, manager)
        users = UserFactory.build_batch(2)
        ctrl.view.prompt_select_user = MagicMock(return_value="invalid")

        with patch.object(UserService, "get_all", return_value=[*users, manager]):
            signal = ctrl.handle_delete()

        assert signal == NavSignal.STAY
