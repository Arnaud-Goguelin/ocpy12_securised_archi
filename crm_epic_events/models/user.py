import uuid

from typing import TYPE_CHECKING

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crm_epic_events.models.database import Base
from crm_epic_events.utils.constants import Roles


if TYPE_CHECKING:
    from crm_epic_events.models.contract import Contract
    from crm_epic_events.models.customer import Customer
    from crm_epic_events.models.event import Event

logger = __import__("logging").getLogger(__name__)


class User(Base):
    """
    Represents a user from Epic Events Company in the system.
    This is just the model to register a user in DB.
    All business logic related to a User is handled in the service layer.


    :ivar id: Unique identifier for the user [PK].
    :type id: uuid.UUID
    :ivar customers: Relationship defining one-to-many association between User and Customer.
        A user can have multiple customers [FK - one-to-many].
    :type customers: list[Customer]
    :ivar contracts: Relationship defining one-to-many association between User and Contract.
        A user can be associated with multiple contracts [FK - one-to-many].
    :type contracts: list[Contract]
    :ivar events: Relationship defining one-to-many association between User and Event.
        A user can be responsible for handling multiple events [FK - one-to-many].
    :type events: list[Event]
    :ivar email: Email address of the user which should be unique across all users.
    :type email: str
    :ivar password: Password for the user used for authentication (should be hashed).
    :type password: str
    :ivar role: role assigned to the user within the system.
    :type role: Roles
    :ivar first_name: The first name of the user.
    :type first_name: str
    :ivar last_name: The last name of the user.
    :type last_name: str
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
