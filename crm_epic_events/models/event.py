import uuid

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from crm_epic_events.models.database import Base
from crm_epic_events.services.event.schemas import EventUpdateInput


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

    @classmethod
    def get_all(cls, db: "Session") -> list["Event"]:
        query = select(cls)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_by_id(cls, event_id: uuid.UUID, db: "Session") -> "Event | None":
        query = select(cls).filter_by(id=event_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    def get_all_without_support(cls, db: "Session") -> list["Event"]:
        query = select(cls).where(cls.support_id.is_(None))
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_all_by_support(cls, support_id: uuid.UUID, db: "Session") -> list["Event"]:
        query = select(cls).filter_by(support_id=support_id)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def create(
        cls,
        contract_id: uuid.UUID,
        customer_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        location: str,
        attendees: int,
        db: "Session",
        support_id: uuid.UUID | None = None,
        notes: str | None = None,
    ) -> "Event":
        event = cls(
            contract_id=contract_id,
            customer_id=customer_id,
            support_id=support_id,
            start_date=start_date,
            end_date=end_date,
            location=location,
            attendees=attendees,
            notes=notes,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        return event

    def update(self, data: EventUpdateInput, db: "Session") -> "Event":
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(self, key, value)
        db.flush()
        db.refresh(self)
        return self

    def delete(self, db: "Session") -> None:
        db.delete(self)
        db.flush()
