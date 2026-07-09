import uuid

from pydantic import BaseModel, EmailStr


# --- Input schemas ---


class CustomerCreateInput(BaseModel):
    """
    Input schema for creating a new customer.

    Automatically assigns the salesperson from the authenticated user.
    If no company matches the given VAT number, one is created using `company_name`.
    Used in: ``CustomerService.create()``.
    """

    salesperson_id: uuid.UUID
    vat_number: str
    company_name: str | None = None  # used for auto-creation if company not found
    email: EmailStr
    first_name: str
    last_name: str
    phone: str


class CustomerUpdateInput(BaseModel):
    """
    Input schema for partially updating an existing customer.

    All fields are optional; only provided fields are applied.
    Used in: ``CustomerService.update()``.
    """

    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
