from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class AccessLinkBase(BaseModel):
    """Base access link schema"""

    consultant_id: int = Field(gt=0)


class AccessLinkCreate(AccessLinkBase):
    """Schema for creating an access link"""

    validity_hours: int = Field(default=72, ge=1, le=168)


class AccessLinkResponse(AccessLinkBase):
    """Schema for access link response"""

    id: int
    token: str
    expires_at: datetime
    created_by_admin_id: int
    is_used: bool
    last_accessed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
