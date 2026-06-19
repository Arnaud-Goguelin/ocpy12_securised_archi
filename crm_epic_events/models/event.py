import uuid

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crm_epic_events.models.database import Base


if TYPE_CHECKING:
    from crm_epic_events.models.contract import Contract
    from crm_epic_events.models.customer import Customer
    from crm_epic_events.models.user import User

logger = __import__("logging").getLogger(__name__)


class Event(Base):
    """
    Represents an event in the system.
    This is just the model to register a user in DB.
    All business logic related to an Event is handled in the service layer.

    :ivar id: Unique identifier for the event.
    :type id: uuid.UUID
    :ivar contract_id: Identifier for the linked contract. Enforces a
        one-to-one relationship with a contract [FK - one-to-one].
    :type contract_id: uuid.UUID
    :ivar contract: The contract associated with the event. Represents a
        one-to-one relationship with the `Contract` entity.
    :type contract: Contract
    :ivar customer_id: Identifier for the customer linked to the event. Represents
        a many-to-one relationship as a customer may have multiple events [FK - many-to-one].
    :type customer_id: uuid.UUID
    :ivar customer: The customer associated with the event.
    :type customer: Customer
    :ivar support_id: Identifier for the support user managing the event [FK - many-to-one].
        This is optional since events may not have an assigned support user.
    :type support_id: uuid.UUID | None
    :ivar support: The support user assigned to handle the event.
    :type support: User | None
    :ivar start_date: Start date and time of the event.
    :type start_date: datetime with timezone
    :ivar end_date: End date and time of the event.
    :type end_date: datetime
    :ivar location: Physical or virtual location where the event is hosted.
    :type location: str
    :ivar attendees: Number of attendees expected to join the event.
    :type attendees: int
    :ivar notes: Additional notes or remarks associated with the event.
    :type notes: str | None
    """

    __tablename__ = "events"

    # --- primary key ---
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # --- relationships ---
    # One-to-One with Contract: one Event is linked to one Contract
    contract_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "contracts.id",
            ondelete="RESTRICT",  # forbidden to delete a Contract if it has a linked Event
        ),
        unique=True,  # enforces one-to-one
    )
    contract: Mapped["Contract"] = relationship(
        "Contract",
        back_populates="event",
        passive_deletes=True,
    )

    # Many-to-One with Customer: one Customer has many Events
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "customers.id",
            ondelete="RESTRICT",
        ),
    )
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="events",
        passive_deletes=True,
    )

    # Many-to-One with User (support): one support User can handle many Events (nullable: not yet assigned)
    support_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    support: Mapped["User | None"] = relationship(
        "User",
        back_populates="events",
        passive_deletes=True,
    )

    # --- specific attributes ---
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str] = mapped_column(String)
    attendees: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
