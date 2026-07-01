from typing import TYPE_CHECKING

import bcrypt

from crm_epic_events.repositories import UserRepository
from crm_epic_events.services.user.schemas import UserRegisterInput, UserUpdateInput
from crm_epic_events.utils import Roles, db_transaction


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User


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
    def register(data: "UserRegisterInput", db: "Session") -> "User":
        """
        Public registration — no auth required.
        Role defaults to SALES, a MANAGER must assign the real role afterwards.
        """

        existing = UserRepository.get_by_email(data.email, db)
        if existing:
            raise ValueError(f"Email '{data.email}' is already in use.")

        hashed = UserService._hash_password(data.password)
        with db_transaction(db, "Registering user"):
            return UserRepository.create(data.first_name, data.last_name, data.email, hashed, db)

    @staticmethod
    def update_profile(
        current_user: "User",
        target_user: "User",
        data: UserUpdateInput,
        db: "Session",
    ) -> "User":
        """
        A user can update their own profile (not their role).
        A MANAGER can update any user's profile.
        Role changes are handled separately via assign_role().
        """
        is_manager = current_user.role == Roles.MANAGER
        if not is_manager:
            data.role = None

        if data.password:
            data.password = UserService._hash_password(data.password)

        with db_transaction(db, "Updating user profile"):
            return UserRepository.update(target_user, data, db)

    @staticmethod
    def assign_role(
        target_user: "User",
        data: UserUpdateInput,
        db: "Session",
    ) -> "User":
        with db_transaction(db, "Assigning role"):
            return UserRepository.update(target_user, data, db)

    @staticmethod
    def delete(
        target_user: "User",
        db: "Session",
    ) -> None:
        with db_transaction(db, "Deleting user"):
            UserRepository.delete(target_user, db)
