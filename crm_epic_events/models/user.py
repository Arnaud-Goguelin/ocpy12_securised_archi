import uuid

from typing import TYPE_CHECKING

from sqlalchemy import String, Uuid, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from crm_epic_events.models.database import Base
from crm_epic_events.permissions import Roles
from crm_epic_events.services.user.schemas import UserAssignRoleInput, UserUpdateInput


if TYPE_CHECKING:
    from crm_epic_events.models.contract import Contract
    from crm_epic_events.models.customer import Customer
    from crm_epic_events.models.event import Event

logger = __import__("logging").getLogger(__name__)


class User(Base):
    """
    Represents an Epic Events employee with an assigned role (SALES, MANAGER, or SUPPORT).

    Each user may be linked as a salesperson to multiple `Customer` and `Contract` records,
    and as support staff to multiple `Event` records.
    Deleting a user is restricted at the database level as long as any of these records remain linked.
    Passwords are stored hashed (bcrypt); hashing is handled at the service layer.
    The default role at creation is SALES; a MANAGER must assign the actual role afterwards.
    """

    __tablename__ = "users"

    # --- primary key ---
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # --- relationship ---
    # One-to-Many with User: one User has many Customers
    # also define relationship here to access to customers from user object
    customers: Mapped[list["Customer"]] = relationship(
        "Customer",
        back_populates="salesperson",
        passive_deletes=True,
    )

    # One-to-Many with Contract: one User (salesperson) has many Contracts
    contracts: Mapped[list["Contract"]] = relationship(
        "Contract",
        back_populates="salesperson",
        passive_deletes=True,
    )

    # One-to-Many with Event: one User (support) handles many Events
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="support",
        passive_deletes=True,
    )

    # --- specific attributes ---
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[Roles] = mapped_column()
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)

    @classmethod
    def get_by_email(cls, _email: str, db: Session) -> "User | None":
        query = select(cls).filter_by(email=_email)
        result = db.execute(query)
        return result.scalar_one()

    @classmethod
    def get_by_id(cls, _id: uuid.UUID, db: Session) -> "User":
        query = select(cls).filter_by(id=_id)
        result = db.execute(query)
        return result.scalar_one()

    @classmethod
    def get_all(cls, db: "Session") -> list["User"]:
        query = select(cls)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_all_by_role(cls, role: "Roles", db: "Session") -> list["User"]:
        query = select(cls).filter_by(role=role)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def create(cls, first_name: str, last_name: str, email: str, password: str, db: "Session") -> "User":
        user = cls(
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

    def update(self, data: "UserUpdateInput | UserAssignRoleInput", db: "Session") -> "User":
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(self, key, value)
        db.flush()
        db.refresh(self)
        return self

    def delete(self, db: "Session") -> None:
        db.delete(self)
        db.flush()
