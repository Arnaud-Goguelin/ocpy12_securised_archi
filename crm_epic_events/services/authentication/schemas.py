from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_serializer

from crm_epic_events.permissions import Roles


class TokenBase(BaseModel):
    """
    Base schema for JWT token payloads, shared by access and refresh tokens.

    Serializes `exp` as a Unix timestamp and `id` as a string, as required by PyJWT.
    """

    id: UUID
    exp: datetime

    @field_serializer("exp")
    def serialize_exp(self, value: datetime) -> int:
        # PyJWT expect timestamp, not datetime
        return int(value.timestamp())

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class AccessTokenPayload(TokenBase):
    """
    JWT access token payload carrying the authenticated user's identity and role.

    Short-lived; used to identify the current user on each request.
    Used in: ``AuthTokensService.generate_access_token()``.
    """

    email: str
    role: Roles

    model_config = {"use_enum_values": True}


class RefreshTokenPayload(TokenBase):
    """
    JWT refresh token payload carrying only the user's ID.

    Long-lived; used to silently reissue an expired access token.
    Used in: ``AuthTokensService.generate_refresh_token()``, ``AuthService._refresh()``.
    """

    pass
