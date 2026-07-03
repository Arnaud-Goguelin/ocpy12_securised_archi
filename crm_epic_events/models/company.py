import uuid

from typing import TYPE_CHECKING

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from crm_epic_events.models.database import Base
from crm_epic_events.services.company.schemas import CompanyUpdateInput


if TYPE_CHECKING:
    from crm_epic_events.models.customer import Customer

logger = __import__("logging").getLogger(__name__)


class Company(Base):
    """
    Represents a company entity in the data model.
    This is just the model to register a user in DB.
    All business logic related to a Company is handled in the service layer.

    :ivar vat_number: The unique VAT number identifying the company [PK].
    :type vat_number: str
    :ivar customers: A list of customers linked to the company [FK - one-to-many].
    :type customers: list[Customer]
    :ivar name: The name of the company.
    :type name: str
    """

    __tablename__ = "companies"

    # --- primary key ---
    vat_number: Mapped[str] = mapped_column(String, primary_key=True, index=True)

    # --- relationships ---
    # One-to-Many with Customer: one Company has many Customers
    customers: Mapped[list["Customer"]] = relationship(
        "Customer",
        back_populates="company",
        passive_deletes=True,
    )

    # --- specific attributes ---
    name: Mapped[str] = mapped_column(String)

    @classmethod
    def get_by_vat(cls, vat_number: str, db: Session) -> "Company | None":
        query = select(cls).filter_by(vat_number=vat_number)
        result = db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    def get_all(cls, db: Session) -> list["Company"]:
        query = select(cls)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def get_by_customers_salesperson(cls, current_user_id: uuid.UUID, db: Session) -> list["Company"]:
        query = select(cls).join(Customer).filter(Customer.salesperson_id == current_user_id)
        result = db.execute(query)
        return list(result.scalars().all())

    @classmethod
    def create(cls, vat_number: str, name: str, db: Session) -> "Company":
        company = cls(vat_number=vat_number, name=name)
        db.add(company)
        db.flush()
        db.refresh(company)
        return company

    def update(self, data: "CompanyUpdateInput", db: Session) -> "Company":
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(self, key, value)
        db.flush()
        db.refresh(self)
        return self

    def delete(self, db: Session) -> None:
        db.delete(self)
        db.flush()
