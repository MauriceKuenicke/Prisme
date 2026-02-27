from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GeneralCustomizations(BaseModel):
    """General consultant-level customizations used in profile snapshots."""

    role: str | None = Field(default=None, max_length=200)
    focus_areas: list[str] = Field(default_factory=list)
    years_experience: int | None = Field(default=None, ge=0, le=80)
    motto: str | None = Field(default=None, max_length=1000)

    @field_validator("focus_areas")
    @classmethod
    def normalize_focus_areas(cls, value: list[str]) -> list[str]:
        """Normalize list values used in snapshot-level customizations."""
        return [str(item).strip() for item in value if str(item).strip()]


class ProfileContentBase(BaseModel):
    """Reusable profile content payload for create and update operations."""

    profile_name: str = Field(min_length=1, max_length=200)
    selected_block_ids: list[int] = Field(min_length=1)
    customizations: dict[str, dict[str, Any]] = Field(default_factory=dict)
    general_customizations: GeneralCustomizations = Field(default_factory=GeneralCustomizations)
    model_config = ConfigDict(extra="forbid")

    @field_validator("profile_name")
    @classmethod
    def normalize_profile_name(cls, value: str) -> str:
        """Ensure profile names are meaningful after trimming whitespace."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("Profile name cannot be empty.")
        return normalized

    @field_validator("selected_block_ids")
    @classmethod
    def validate_selected_blocks(cls, value: list[int]) -> list[int]:
        """Require positive block ids and remove duplicates while preserving order."""
        normalized: list[int] = []
        seen: set[int] = set()
        for block_id in value:
            if block_id <= 0:
                raise ValueError("selected_block_ids must contain positive integers.")
            if block_id not in seen:
                seen.add(block_id)
                normalized.append(block_id)
        return normalized


class ProfileCreate(ProfileContentBase):
    """Schema for creating a profile."""

    consultant_id: int


class ProfileUpdate(ProfileContentBase):
    """Schema for updating a profile."""


class ProfileResponse(BaseModel):
    """Schema for profile responses."""

    id: int
    consultant_id: int
    profile_name: str
    selected_block_ids: str
    profile_data: str
    created_by_admin_id: int
    created_at: datetime | str
    updated_at: datetime | str

    model_config = ConfigDict(from_attributes=True)
