from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crm_epic_events.models.database import Base


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
