from pydantic import BaseModel


# --- Input schemas ---


class CompanyCreateInput(BaseModel):
    vat_number: str
    name: str


class CompanyUpdateInput(BaseModel):
    name: str | None = None


# --- Output schema ---


class CompanyResponse(BaseModel):
    vat_number: str
    name: str

    model_config = {"from_attributes": True}
