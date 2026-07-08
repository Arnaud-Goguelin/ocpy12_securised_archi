import uuid

from pydantic import BaseModel, EmailStr, field_validator

from crm_epic_events.errors import PasswordNotSecuredError
from crm_epic_events.permissions import Roles


SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;':\",./<>?"


def validate_password(value: str) -> str:

    errors = []
    if len(value) < 12:
        errors.append("at least 12 characters")
    if not any(char.isdigit() for char in value):
        errors.append("at least one digit")
    if not any(char in SPECIAL_CHARS for char in value):
        errors.append("at least one special character")
    if errors:
        raise PasswordNotSecuredError(message=f"Password must contain: {', '.join(errors)}.")
    return value


# --- Input schemas ---


class UserRegisterInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return validate_password(value)


class UserUpdateInput(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: Roles | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return validate_password(value)


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
