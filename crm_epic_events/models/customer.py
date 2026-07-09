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
    Represents a customer belonging to a company and assigned to a salesperson.

    Each customer is linked to exactly one `Company` (via `company_vat`) and one `User` salesperson
    (via `salesperson_id`).
    Deleting either the company or the salesperson is restricted as long as
    customers remain linked to them (``ondelete="RESTRICT"``).
    A customer may have multiple `Contract` and `Event` records.
    Company deletion is cascaded at the service layer when the last customer of a company is removed.
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
