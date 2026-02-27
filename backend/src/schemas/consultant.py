from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime


class ConsultantBase(BaseModel):
    """Base consultant schema"""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    title: str = Field(min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=5000)
    photo_url: str | None = Field(default=None, max_length=500)
    role: str | None = Field(default=None, max_length=200)
    focus_areas: list[str] | None = None
    years_experience: int | None = Field(default=None, ge=0, le=80)
    motto: str | None = Field(default=None, max_length=1000)

    @field_validator("first_name", "last_name", "title", "summary", "photo_url", "role", "motto", mode="before")
    @classmethod
    def strip_string_fields(cls, value: str | None) -> str | None:
        """Normalize optional text values while preserving explicit nulls."""
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("focus_areas")
    @classmethod
    def normalize_focus_areas(cls, value: list[str] | None) -> list[str] | None:
        """Trim focus area entries and drop empty values."""
        if value is None:
            return None
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        return cleaned


class ConsultantCreate(ConsultantBase):
    """Schema for creating a consultant"""

    pass


class ConsultantUpdate(BaseModel):
    """Schema for updating a consultant"""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=5000)
    photo_url: str | None = Field(default=None, max_length=500)
    role: str | None = Field(default=None, max_length=200)
    focus_areas: list[str] | None = None
    years_experience: int | None = Field(default=None, ge=0, le=80)
    motto: str | None = Field(default=None, max_length=1000)

    @field_validator("first_name", "last_name", "title", "summary", "photo_url", "role", "motto", mode="before")
    @classmethod
    def strip_update_string_fields(cls, value: str | None) -> str | None:
        """Trim incoming update strings."""
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("focus_areas")
    @classmethod
    def normalize_update_focus_areas(cls, value: list[str] | None) -> list[str] | None:
        """Trim focus area updates and drop empty values."""
        if value is None:
            return None
        return [str(item).strip() for item in value if str(item).strip()]


class ConsultantResponse(ConsultantBase):
    """Schema for consultant response"""

    id: int
    created_by_admin_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
