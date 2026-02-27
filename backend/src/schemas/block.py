from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Literal


class BlockBase(BaseModel):
    """Base block schema"""

    title: str = Field(min_length=1, max_length=200)
    block_type: Literal["project", "skill", "certification", "misc"]
    order: int = Field(default=0, ge=0, le=10000)


class ProjectBlockCreate(BlockBase):
    """Schema for creating a project block"""

    block_type: Literal["project"] = "project"
    client_name: str | None = Field(default=None, max_length=200)
    project_description: str | None = Field(default=None, max_length=5000)
    role: str | None = Field(default=None, max_length=200)
    technologies: list[str] | str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_ongoing: bool | None = False
    duration_months: int | None = Field(default=None, ge=0, le=1200)


class SkillBlockCreate(BlockBase):
    """Schema for creating a skill block"""

    block_type: Literal["skill"] = "skill"
    proficiency_level: str | None = Field(default=None, max_length=50)


class CertificationBlockCreate(BlockBase):
    """Schema for creating a certification block"""

    block_type: Literal["certification"] = "certification"
    issuing_organization: str | None = Field(default=None, max_length=200)
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = Field(default=None, max_length=200)
    credential_url: str | None = Field(default=None, max_length=500)


class MiscBlockCreate(BlockBase):
    """Schema for creating a misc block"""

    block_type: Literal["misc"] = "misc"
    misc_content: str | None = Field(default=None, max_length=5000)


# Union type for creating any block
BlockCreate = ProjectBlockCreate | SkillBlockCreate | CertificationBlockCreate | MiscBlockCreate


class BlockUpdate(BaseModel):
    """Schema for updating a block"""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    order: int | None = Field(default=None, ge=0, le=10000)
    # Type-specific fields
    client_name: str | None = Field(default=None, max_length=200)
    project_description: str | None = Field(default=None, max_length=5000)
    role: str | None = Field(default=None, max_length=200)
    technologies: list[str] | str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_ongoing: bool | None = None
    duration_months: int | None = Field(default=None, ge=0, le=1200)
    proficiency_level: str | None = Field(default=None, max_length=50)
    misc_content: str | None = Field(default=None, max_length=5000)
    issuing_organization: str | None = Field(default=None, max_length=200)
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = Field(default=None, max_length=200)
    credential_url: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(extra="forbid")


class BlockResponse(BaseModel):
    """Schema for block response"""

    id: int
    consultant_id: int
    block_type: str
    title: str
    order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Type-specific fields (all optional)
    client_name: str | None = None
    project_description: str | None = None
    role: str | None = None
    technologies: list[str] | str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_ongoing: bool | None = None
    duration_months: int | None = None
    proficiency_level: str | None = None
    misc_content: str | None = None
    issuing_organization: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = None
    credential_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BlockReorderRequest(BaseModel):
    """Schema for reordering blocks"""

    block_orders: list[dict[str, int]] = Field(min_length=1)  # [{"id": 1, "order": 0}, ...]
