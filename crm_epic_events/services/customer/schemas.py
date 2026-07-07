import uuid

from datetime import datetime

from pydantic import BaseModel, EmailStr


# --- Input schemas ---


class CustomerCreateInput(BaseModel):
    salesperson_id: uuid.UUID
    vat_number: str
    company_name: str | None = None  # used for auto-creation if company not found
    email: EmailStr
    first_name: str
    last_name: str
    phone: str


class CustomerUpdateInput(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None


# --- Output schema ---


class CustomerResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    company_name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
