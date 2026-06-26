# schemas.py (dans ton module authentication)
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from crm_epic_events.utils import Roles


class AccessTokenPayload(BaseModel):
    id: UUID
    email: str
    role: Roles
    exp: datetime

    model_config = {"use_enum_values": True}  # sérialise Roles en str dans le JWT


class RefreshTokenPayload(BaseModel):
    id: UUID
    exp: datetime
