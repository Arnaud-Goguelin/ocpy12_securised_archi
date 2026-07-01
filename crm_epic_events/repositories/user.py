import uuid

from typing import TYPE_CHECKING

from sqlalchemy import select

from crm_epic_events.models.user import User
from crm_epic_events.services.user.schemas import UserUpdateInput
from crm_epic_events.utils import Roles


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class UserRepository:
    @staticmethod
    def get_all(db: "Session") -> list[User]:
        query = select(User)
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_all_by_role(role: Roles, db: "Session") -> list[User]:
        query = select(User).filter_by(role=role)
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_by_id(_id: uuid.UUID, db: "Session") -> User | None:
        query = select(User).filter_by(id=_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_email(email: str, db: "Session") -> User | None:
        query = select(User).filter_by(email=email)
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def create(first_name: str, last_name: str, email: str, password: str, db: "Session") -> User:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=Roles.SALES,  # default role, MANAGER assigns the real role after
        )
        db.add(user)
        db.flush()
        db.refresh(user)
        return user

    @staticmethod
    def update(user: User, data: UserUpdateInput, db: "Session") -> User:
        for key, value in data.model_dump().items():
            setattr(user, key, value)
        db.flush()
        db.refresh(user)
        return user

    @staticmethod
    def delete(user: User, db: "Session") -> None:
        db.delete(user)
        db.flush()
