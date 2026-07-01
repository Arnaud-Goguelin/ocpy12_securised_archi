from typing import TYPE_CHECKING

import bcrypt

from crm_epic_events.errors import UserIsNotOwnerError, UserNotAllowedError
from crm_epic_events.repositories import UserRepository


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User
    from crm_epic_events.utils import Roles, db_transaction


class UserService:
    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def get_all(db: "Session") -> list["User"]:
        return UserRepository.get_all(db)

    @staticmethod
    def get_all_by_role(role: "Roles", db: "Session") -> list["User"]:
        return UserRepository.get_all_by_role(role, db)

    @staticmethod
    def register(first_name: str, last_name: str, email: str, password: str, db: "Session") -> "User":
        """
        Public registration — no auth required.
        Role defaults to SALES, a MANAGER must assign the real role afterwards.
        """

        existing = UserRepository.get_by_email(email, db)
        if existing:
            raise ValueError(f"Email '{email}' is already in use.")

        hashed = UserService._hash_password(password)
        with db_transaction(db, "Registering user"):
            return UserRepository.create(first_name, last_name, email, hashed, db)

    @staticmethod
    def update_profile(
        current_user: "User",
        target_user: "User",
        data: dict,
        db: "Session",
    ) -> "User":
        """
        A user can update their own profile (not their role).
        A MANAGER can update any user's profile (not their role).
        Role changes are handled separately via assign_role().
        """
        data.pop("role", None)  # role change is never allowed here

        is_manager = current_user.role == Roles.MANAGER
        is_self = current_user.id == target_user.id

        if not is_manager and not is_self:
            raise UserIsNotOwnerError()

        if "password" in data:
            data["password"] = UserService._hash_password(data["password"])

        with db_transaction(db, "Updating user profile"):
            return UserRepository.update(target_user, data, db)

    @staticmethod
    def assign_role(
        current_user: "User",
        target_user: "User",
        role: Roles,
        db: "Session",
    ) -> "User":
        """MANAGER only — assigns a role to any user."""
        if current_user.role != Roles.MANAGER:
            raise UserNotAllowedError()
        with db_transaction(db, "Assigning role"):
            return UserRepository.update(target_user, {"role": role}, db)

    @staticmethod
    def delete(
        current_user: "User",
        target_user: "User",
        db: "Session",
    ) -> None:
        """MANAGER only."""
        if current_user.role != Roles.MANAGER:
            raise UserNotAllowedError()
        with db_transaction(db, "Deleting user"):
            UserRepository.delete(target_user, db)
