import bcrypt
import pytest

from crm_epic_events.errors import PasswordNotSecuredError, UserAlreadyExistsError
from crm_epic_events.services.user.schemas import UserAssignRoleInput, UserRegisterInput, UserUpdateInput
from crm_epic_events.services.user.service import UserService
from crm_epic_events.utils.constants import Roles
from tests.factories import SECURED_RAW_PASSWORD, UNSECURED_RAW_PASSWORD, UserDBFactory, fake


# ── get_all ───────────────────────────────────────────────────────────────────


class TestGetAll:
    def test_returns_all_users(self, db_session):
        UserDBFactory.create_batch(3)
        result = UserService.get_all(db_session)
        assert len(result) == 3

    def test_returns_empty_list(self, db_session):
        result = UserService.get_all(db_session)
        assert result == []


# ── get_all_by_role ───────────────────────────────────────────────────────────


class TestGetAllByRole:
    def test_returns_only_users_with_given_role(self, db_session):
        UserDBFactory.create_batch(2, role=Roles.MANAGER)
        result = UserService.get_all_by_role(Roles.MANAGER, db_session)
        assert len(result) == 2
        assert all(u.role == Roles.MANAGER for u in result)

    def test_returns_empty_list_when_no_match(self, db_session):
        UserDBFactory(role=Roles.SALES)
        result = UserService.get_all_by_role(Roles.SUPPORT, db_session)
        assert result == []


# ── register ──────────────────────────────────────────────────────────────────


class TestRegister:
    def test_creates_and_returns_user(self, db_session, register_data):
        user = UserService.register(register_data, db_session)
        assert user.first_name == register_data.first_name
        assert user.last_name == register_data.last_name
        assert user.email == register_data.email

    def test_user_is_persisted(self, db_session, register_data):
        user = UserService.register(register_data, db_session)
        result = UserService.get_all(db_session)
        assert any(u.id == user.id for u in result)

    def test_default_role_is_sales(self, db_session, register_data):
        user = UserService.register(register_data, db_session)
        assert user.role == Roles.SALES

    def test_password_is_hashed(self, db_session, register_data):
        user = UserService.register(register_data, db_session)
        assert bcrypt.checkpw(SECURED_RAW_PASSWORD.encode(), user.password.encode())

    def test_raises_if_email_already_exists(self, db_session, register_data):
        UserService.register(register_data, db_session)
        with pytest.raises(UserAlreadyExistsError):
            UserService.register(register_data, db_session)

    def test_raises_if_password_not_secured(self):
        with pytest.raises(PasswordNotSecuredError):
            UserRegisterInput(
                first_name="John",
                last_name="Doe",
                email=fake.email(),
                password=UNSECURED_RAW_PASSWORD,
            )


# ── update_profile ────────────────────────────────────────────────────────────


class TestUpdateProfile:
    def test_manager_can_update_target_user(self, db_session, manager, salesperson):
        data = UserUpdateInput(first_name="New first name")
        updated = UserService.update_profile(manager, salesperson, data, db_session)
        assert updated.first_name == "New first name"

    def test_non_manager_updates_only_self(self, db_session, salesperson, support):
        data = UserUpdateInput(first_name="New first name")
        updated = UserService.update_profile(salesperson, salesperson, data, db_session)
        assert updated.first_name == "New first name"

        assert salesperson.first_name == "New first name"
        assert support.first_name == support.first_name

    def test_non_manager_cannot_change_role(self, db_session):
        sales = UserDBFactory(role=Roles.SALES)
        data = UserUpdateInput(role=Roles.MANAGER)
        updated = UserService.update_profile(sales, sales, data, db_session)
        assert updated.role == Roles.SALES

    def test_manager_can_change_role(self, db_session):
        manager = UserDBFactory(role=Roles.MANAGER)
        target = UserDBFactory(role=Roles.SALES)
        data = UserUpdateInput(role=Roles.SUPPORT)
        updated = UserService.update_profile(manager, target, data, db_session)
        assert updated.role == Roles.SUPPORT

    def test_password_is_hashed_on_update(self, db_session):
        user = UserDBFactory(role=Roles.SALES)
        data = UserUpdateInput(password=SECURED_RAW_PASSWORD)
        updated = UserService.update_profile(user, user, data, db_session)
        assert bcrypt.checkpw(SECURED_RAW_PASSWORD.encode(), updated.password.encode())

    def test_raises_if_password_not_secured(self):
        with pytest.raises(PasswordNotSecuredError):
            UserUpdateInput(password=UNSECURED_RAW_PASSWORD)


# ── assign_role ───────────────────────────────────────────────────────────────


class TestAssignRole:
    def test_assigns_role_to_user(self, db_session):
        target = UserDBFactory(role=Roles.SALES)
        data = UserAssignRoleInput(role=Roles.SUPPORT)
        updated = UserService.assign_role(target, data, db_session)
        assert updated.role == Roles.SUPPORT

    def test_assignment_is_persisted(self, db_session, salesperson):
        data = UserAssignRoleInput(role=Roles.MANAGER)
        UserService.assign_role(salesperson, data, db_session)
        result = UserService.get_all_by_role(Roles.MANAGER, db_session)
        assert any(u.id == salesperson.id for u in result)


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_deletes_user(self, db_session, salesperson):
        UserService.delete(salesperson, db_session)
        result = UserService.get_all(db_session)
        assert not any(u.id == salesperson.id for u in result)

    def test_delete_returns_none(self, db_session, salesperson):
        result = UserService.delete(salesperson, db_session)
        assert result is None
