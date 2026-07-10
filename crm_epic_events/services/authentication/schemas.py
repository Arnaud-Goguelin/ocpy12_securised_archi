from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_serializer


class TokenBase(BaseModel):
    """
    Base schema for JWT token payloads, used as access and refresh tokens.

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
