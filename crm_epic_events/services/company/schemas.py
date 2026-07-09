from pydantic import BaseModel


# --- Input schemas ---


class CompanyCreateInput(BaseModel):
    """
    Input schema for creating a new company.

    Used in: ``CompanyService.create()``.
    Also accepted alongside ``CustomerCreateInput`` in ``CompanyService.create()`` for auto-creation.
    """

    vat_number: str
    name: str


class CompanyUpdateInput(BaseModel):
    """
    Input schema for partially updating an existing company.

    Only `name` can be updated; VAT number is immutable.
    Used in: ``CompanyService.update()``.
    """

    name: str | None = None
