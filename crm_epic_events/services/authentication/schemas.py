from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_serializer

from crm_epic_events.utils import Roles


class TokenBase(BaseModel):
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
    email: str
    role: Roles

    model_config = {"use_enum_values": True}


class RefreshTokenPayload(TokenBase):
    pass
