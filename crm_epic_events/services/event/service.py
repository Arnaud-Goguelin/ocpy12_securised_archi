import uuid

from typing import TYPE_CHECKING

from crm_epic_events.errors import ContractNotFoundError, ContractNotSignedError
from crm_epic_events.models import Contract, Event
from crm_epic_events.utils import db_transaction


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User
    from crm_epic_events.services.event.schemas import EventCreateInput, EventUpdateInput


class EventService:
    """Handles business logic for event lifecycle management."""

    @staticmethod
    def get_all(db: "Session") -> list["Event"]:
        return Event.get_all(db)

    @staticmethod
    def get_all_without_support(db: "Session") -> list["Event"]:
        """Management filter: events with no support contact assigned."""
        return Event.get_all_without_support(db)

    @staticmethod
    def get_all_by_support(current_user: "User", db: "Session") -> list["Event"]:
        """Support filter: events assigned to the current support user."""
        return Event.get_all_by_support(current_user.id, db)

    @staticmethod
    def get_by_id(event_id: uuid.UUID, db: "Session") -> "Event | None":
        return Event.get_by_id(event_id, db)

    @staticmethod
    def create(data: "EventCreateInput", db: "Session") -> "Event":
        """
        Creates a new event linked to a signed contract. Restricted to SALES only.

        Ownership and permission checks are delegated to the controller.

        Raises:
            ContractNotFoundError: If no contract matches `data.contract_id`.
            ContractNotSignedError: If the linked contract has not been signed yet.
        """

        contract = Contract.get_by_id(data.contract_id, db)
        if not contract:
            raise ContractNotFoundError()
        if not contract.status:
            raise ContractNotSignedError()

        with db_transaction(db, "Creating event"):
            return Event.create(
                contract_id=data.contract_id,
                customer_id=data.customer_id,
                support_id=data.support_id,
                start_date=data.start_date,
                end_date=data.end_date,
                location=data.location,
                attendees=data.attendees,
                notes=data.notes,
                db=db,
            )

    @staticmethod
    def update(target_event: "Event", data: "EventUpdateInput", db: "Session") -> "Event":
        with db_transaction(db, "Updating event"):
            return target_event.update(data, db)

    @staticmethod
    def delete(target_event: "Event", db: "Session") -> None:
        with db_transaction(db, "Deleting event"):
            target_event.delete(db)
