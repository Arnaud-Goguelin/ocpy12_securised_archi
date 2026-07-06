import uuid
from typing import TYPE_CHECKING

from crm_epic_events.models import Event
from crm_epic_events.utils import db_transaction

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from crm_epic_events.models import User
    from crm_epic_events.services.event.schemas import EventCreateInput, EventUpdateInput


class EventService:
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
        Only SALES members can create an event, for a customer they own
        with a signed contract. Permission checks are done in the controller.
        """
        with db_transaction(db, "Creating event"):
            return Event.create(
                contract_id=data.contract_id,
                customer_id=data.customer_id,
                support_contact_id=data.support_contact_id,
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
