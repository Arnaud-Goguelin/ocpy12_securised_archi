import uuid

from pydantic import BaseModel, EmailStr, field_validator

from crm_epic_events.utils.constants import Roles


# --- Input schemas ---


class UserRegisterInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return value


class UserUpdateInput(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: Roles | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value: str | None) -> str | None:
        if value is not None and len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return value


class UserAssignRoleInput(BaseModel):
    role: Roles


# --- Output schema ---


class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    role: Roles

    model_config = {"from_attributes": True}
