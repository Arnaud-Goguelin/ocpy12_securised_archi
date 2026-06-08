import uuid

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crm_epic_events.models.database import Base


if TYPE_CHECKING:
    from crm_epic_events.models.user import User


logger = __import__("logging").getLogger(__name__)


class Customer(Base):
    """ """

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
            ondelete="RESTRICT", # it is forbidden to delete a User if it has linked Customers
        ),
    )
    salesperson: Mapped["User"] = relationship(
        "User",
        back_populates="customers",
        passive_deletes=True,
    )

    # --- specific attributes ---
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
