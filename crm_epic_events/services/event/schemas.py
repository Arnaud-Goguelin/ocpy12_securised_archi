import uuid

from datetime import datetime

from pydantic import BaseModel, model_validator


# --- Input schemas ---


class EventCreateInput(BaseModel):
    """
    Input schema for creating a new event.

    Requires a signed contract; validation that the contract is signed is enforced at the service layer.
    Cross-field validation ensures `end_date` is not before `start_date`.
    Support assignment is optional at creation time.
    Used in: ``EventService.create()``.
    """

    contract_id: uuid.UUID
    customer_id: uuid.UUID
    support_id: uuid.UUID | None = None
    start_date: datetime
    end_date: datetime
    location: str
    attendees: int
    notes: str | None = None

    @model_validator(mode="after")
    def end_after_start(self) -> "EventCreateInput":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class EventUpdateInput(BaseModel):
    """
    Input schema for partially updating an existing event.

    All fields are optional; only provided fields are applied.
    Cross-field validation ensures `end_date` is not before `start_date` when both are provided.
    Used in: ``EventService.update()``.
    """

    support_id: uuid.UUID | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    location: str | None = None
    attendees: int | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def end_after_start(self) -> "EventUpdateInput":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
