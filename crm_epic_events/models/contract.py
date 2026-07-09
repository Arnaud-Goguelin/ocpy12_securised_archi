import uuid

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, Uuid, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from crm_epic_events.models.database import Base
from crm_epic_events.services.contract.schemas import ContractUpdateInput


if TYPE_CHECKING:
    from crm_epic_events.models.customer import Customer
    from crm_epic_events.models.event import Event
    from crm_epic_events.models.user import User

logger = __import__("logging").getLogger(__name__)


class Contract(Base):
    """
    Represents a commercial contract between a customer and Epic Events.

    Each contract is linked to one `Customer` and inherits the customer's salesperson as its own.
    A contract may optionally be associated with one `Event` (one-to-one).
    Deleting a linked customer or salesperson is restricted at the database level as long as contracts remain.
    Tracks financial state via `total_amount` and `remaining_amount`, and signature state via `status`.
    """

    __tablename__ = "contracts"

    # --- primary key ---
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # --- relationships ---
    # Many-to-One with Customer: one Customer has many Contracts
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "customers.id",
            ondelete="RESTRICT",  # forbidden to delete a Customer if it has linked Contracts
        ),
    )
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="contracts",
        passive_deletes=True,
    )

    # Many-to-One with User (salesperson): one User has many Contracts
    salesperson_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",  # forbidden to delete a User if it has linked Contracts
        ),
    )
    salesperson: Mapped["User"] = relationship(
        "User",
        back_populates="contracts",
        passive_deletes=True,
    )

    # One-to-One with Event: one Contract has one Event
    event: Mapped["Event | None"] = relationship(
        "Event",
        back_populates="contract",
        passive_deletes=True,
        uselist=False,
    )

    # --- specific attributes ---
    total_amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    remaining_amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    status: Mapped[bool] = mapped_column(Boolean, default=False)

    # --- Queries ---

    @classmethod
    def get_all(cls, db: "Session") -> list["Contract"]:
        query = select(cls)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_by_id(cls, contract_id: uuid.UUID, db: "Session") -> "Contract | None":
        return db.get(cls, contract_id)

    @classmethod
    def get_all_by_salesperson(cls, salesperson_id: uuid.UUID, db: "Session") -> list["Contract"]:
        query = select(cls).filter_by(salesperson_id=salesperson_id)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_unsigned(cls, db: "Session") -> list["Contract"]:
        query = select(cls).filter_by(status=False)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_unpaid(cls, db: "Session") -> list["Contract"]:
        query = select(cls).where(cls.remaining_amount > 0)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def create(
        cls,
        customer_id: uuid.UUID,
        salesperson_id: uuid.UUID,
        total_amount: Decimal,
        remaining_amount: Decimal,
        status: bool,
        db: "Session",
    ) -> "Contract":
        contract = cls(
            customer_id=customer_id,
            salesperson_id=salesperson_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            status=status,
        )
        db.add(contract)
        db.flush()
        db.refresh(contract)
        return contract

    def update(self, data: ContractUpdateInput, db: "Session") -> "Contract":
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(self, key, value)
        db.flush()
        db.refresh(self)
        return self

    def delete(self, db: "Session") -> None:
        db.delete(self)
        db.flush()
