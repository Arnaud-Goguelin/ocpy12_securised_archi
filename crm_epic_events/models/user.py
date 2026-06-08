import uuid

from typing import TYPE_CHECKING

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crm_epic_events.models.database import Base
from crm_epic_events.utils.constants import Roles


if TYPE_CHECKING:
    from crm_epic_events.models.customer import Customer

logger = __import__("logging").getLogger(__name__)


class User(Base):
    """ """

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

    # --- specific attributes ---
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[Roles] = mapped_column()
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
