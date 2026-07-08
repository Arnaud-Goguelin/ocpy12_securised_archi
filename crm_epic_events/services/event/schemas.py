import uuid

from datetime import datetime

from pydantic import BaseModel, model_validator


# --- Input schemas ---


class EventCreateInput(BaseModel):
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


# --- Output schema ---


class EventResponse(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    customer_id: uuid.UUID
    support_id: uuid.UUID | None
    start_date: datetime
    end_date: datetime
    location: str
    attendees: int
    notes: str | None

    model_config = {"from_attributes": True}
