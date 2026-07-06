import contextlib

from typing import TYPE_CHECKING

import bcrypt

from sqlalchemy.exc import NoResultFound

from crm_epic_events.errors import UserAlreadyExistsError
from crm_epic_events.models import User
from crm_epic_events.utils import Roles, db_transaction


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.services.user.schemas import UserAssignRoleInput, UserRegisterInput, UserUpdateInput


class UserService:
    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # get_all and gat_all_by_role directly delegate to model's methods
    # but we keep them here for consistency with other services (controller always calls service, not model directly)
    @staticmethod
    def get_all(db: "Session") -> list["User"]:
        return User.get_all(db)

    @staticmethod
    def get_all_by_role(role: "Roles", db: "Session") -> list["User"]:
        return User.get_all_by_role(role, db)

    @staticmethod
    def register(data: "UserRegisterInput", db: "Session") -> "User":
        """
        Public registration — no auth required.
        Role defaults to SALES, a MANAGER must assign the real role afterwards.
        """

        with contextlib.suppress(NoResultFound):
            user = User.get_by_email(data.email, db)

        if user:
            raise UserAlreadyExistsError()

        hashed = UserService._hash_password(data.password)
        with db_transaction(db, "Registering user"):
            return User.create(data.first_name, data.last_name, data.email, hashed, db)

    @staticmethod
    def update_profile(
        current_user: "User",
        target_user: "User",
        data: "UserUpdateInput",
        db: "Session",
    ) -> "User":
        """
        A user can update their own profile (not their role).
        A MANAGER can update any user's profile.
        Role changes are handled separately via assign_role().
        """
        if current_user.role != Roles.MANAGER:
            data.role = None
            user_to_update = current_user
        else:
            user_to_update = target_user

        if data.password:
            data.password = UserService._hash_password(data.password)

        with db_transaction(db, "Updating user profile"):
            return user_to_update.update(data, db)

    @staticmethod
    def assign_role(
        target_user: "User",
        data: "UserAssignRoleInput",
        db: "Session",
    ) -> "User":
        with db_transaction(db, "Assigning role"):
            return target_user.update(data, db)

    @staticmethod
    def delete(
        target_user: "User",
        db: "Session",
    ) -> None:
        with db_transaction(db, "Deleting user"):
            target_user.delete(db)
