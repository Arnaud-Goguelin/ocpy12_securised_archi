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
    Representation of a Contract entity.
    This is just the model to register a user in DB.
    All business logic related to a Contract is handled in the service layer.

    :ivar id: The unique identifier for the contract [PK].
    :type id: uuid.UUID
    :ivar customer_id: The identifier linking the contract to its associated customer [FK - many-to-one].
    :type customer_id: uuid.UUID
    :ivar customer: The customer associated with this contract.
    :type customer: Customer
    :ivar salesperson_id: The identifier linking the contract to its assigned salesperson [FK - many-to-one].
    :type salesperson_id: uuid.UUID
    :ivar salesperson: The salesperson associated with this contract.
    :type salesperson: User
    :ivar event: The event associated with this contract, if any [FK - one-to-one].
    :type event: Event or None
    :ivar total_amount: The total monetary value of the contract.
    :type total_amount: float
    :ivar remaining_amount: The remaining balance yet to be paid on the contract.
    :type remaining_amount: float
    :ivar created_at: The timestamp indicating when the contract was created.
    :type created_at: datetime
    :ivar status: The status of the contract, indicating whether it is signed (True) or not (False).
    :type status: bool
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

    @staticmethod
    def get_all(db: Session) -> list["Contract"]:
        return list(db.execute(select(Contract)).scalars().all())

    @staticmethod
    def get_by_id(contract_id: str, db: Session) -> "Contract | None":
        return db.get(Contract, contract_id)

    @staticmethod
    def get_all_by_salesperson(salesperson_id: str, db: Session) -> list["Contract"]:
        return list(db.execute(select(Contract).where(Contract.salesperson_id == salesperson_id)).scalars().all())

    @staticmethod
    def get_unsigned(db: Session) -> list["Contract"]:
        return list(
            db.execute(select(Contract).where(Contract.status == False)).scalars().all()  # noqa: E712
        )

    @staticmethod
    def get_unpaid(db: Session) -> list["Contract"]:
        return list(db.execute(select(Contract).where(Contract.remaining_amount > 0)).scalars().all())

    @staticmethod
    def create(
        customer_id: str,
        salesperson_id: str,
        total_amount: float,
        remaining_amount: float,
        status: bool,
        db: Session,
    ) -> "Contract":
        contract = Contract(
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

    def update(self, data: "ContractUpdateInput", db: Session) -> "Contract":
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(self, field, value)
        db.flush()
        db.refresh(self)
        return self

    def delete(self, db: Session) -> None:
        db.delete(self)
        db.flush()
