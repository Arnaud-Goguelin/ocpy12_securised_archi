import uuid

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from crm_epic_events.models.database import Base
from crm_epic_events.services.customer.schemas import CustomerUpdateInput


if TYPE_CHECKING:
    from crm_epic_events.models.company import Company
    from crm_epic_events.models.contract import Contract
    from crm_epic_events.models.event import Event
    from crm_epic_events.models.user import User


logger = __import__("logging").getLogger(__name__)


class Customer(Base):
    """
    Represents a Customer entity with relationships and specific attributes.
    This is just the model to register a user in DB.
    All business logic related to a Customer is handled in the service layer.

    :ivar id: Unique identifier for the Customer.
    :type id: uuid.UUID
    :ivar salesperson_id: Identifier of the User associated as salesperson to the Customer [FK - many-to-one].
    :type salesperson_id: uuid.UUID
    :ivar salesperson: References the User who is the salesperson for the Customer.
    :type salesperson: User
    :ivar company_vat: VAT number of the Company associated with the Customer.
    :type company_vat: str
    :ivar company: References the Company associated with the Customer.
    :type company: Company
    :ivar contracts: List of contracts associated with the Customer [FK - one-to-many].
    :type contracts: list[Contract]
    :ivar events: List of events associated with the Customer [FK - one-to-many].
    :type events: list[Event]
    :ivar email: Email address of the Customer.
    :type email: str
    :ivar password: Password for the Customer's account.
    :type password: str
    :ivar first_name: First name of the Customer.
    :type first_name: str
    :ivar last_name: Last name of the Customer.
    :type last_name: str
    :ivar phone: Phone number of the Customer.
    :type phone: str
    :ivar created_at: Timestamp of when the Customer was created.
    :type created_at: datetime with timezone
    :ivar last_updated_at: Timestamp of when the Customer was last updated.
    :type last_updated_at: datetime with timezone
    """

    __tablename__ = "customers"

    # --- primary key ---
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # --- relationship ---
    # One-to-Many with User: one User has many Customers
    salesperson_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",  # it is forbidden to delete a User if it has linked Customers
        ),
    )
    salesperson: Mapped["User"] = relationship(
        "User",
        back_populates="customers",
        passive_deletes=True,
    )

    # Many-to-One with Company: one Company has many Customers
    company_vat: Mapped[str] = mapped_column(
        String,
        ForeignKey(
            "companies.vat_number",
            ondelete="RESTRICT",
        ),
    )
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="customers",
        passive_deletes=True,
    )

    # One-to-Many with Contract: one Customer has many Contracts
    contracts: Mapped[list["Contract"]] = relationship(
        "Contract",
        back_populates="customer",
        passive_deletes=True,
    )

    # One-to-Many with Event: one Customer has many Events
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="customer",
        passive_deletes=True,
    )

    # --- specific attributes ---
    email: Mapped[str] = mapped_column(String, unique=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    @classmethod
    def get_all(cls, db: "Session") -> list["Customer"]:
        query = select(cls)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_all_by_salesperson(cls, salesperson_id: uuid.UUID, db: "Session") -> list["Customer"]:
        query = select(cls).filter_by(salesperson_id=salesperson_id)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_all_by_company_vat(cls, company_vat: str, db: "Session") -> list["Customer"]:
        query = select(cls).filter_by(company_vat=company_vat)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def create(
        cls,
        salesperson_id: uuid.UUID,
        company_vat: str,
        email: str,
        first_name: str,
        last_name: str,
        phone: str,
        db: "Session",
    ) -> "Customer":
        customer = cls(
            salesperson_id=salesperson_id,
            company_vat=company_vat,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        db.add(customer)
        db.flush()
        db.refresh(customer)
        return customer

    def update(self, data: CustomerUpdateInput, db: "Session") -> "Customer":
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(self, key, value)
        db.flush()
        db.refresh(self)
        return self

    def delete(self, db: "Session") -> None:
        db.delete(self)
        db.flush()
