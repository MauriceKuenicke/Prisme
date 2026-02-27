from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime


class AdminBase(BaseModel):
    """Base admin schema"""

    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        """Normalize and validate admin usernames."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("Username cannot be empty.")
        return normalized


class AdminCreate(AdminBase):
    """Schema for creating an admin"""

    password: str = Field(min_length=8, max_length=128)
    is_super_admin: bool = False


class AdminUpdate(BaseModel):
    """Schema for updating an admin"""

    username: str | None = Field(default=None, min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None


class AdminResponse(AdminBase):
    """Schema for admin response"""

    id: int
    is_active: bool
    is_super_admin: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Token response schema"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""

    username: str | None = None


class LoginRequest(BaseModel):
    """Login request schema"""

    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class AdminProfileUpdate(BaseModel):
    """Schema for updating own admin profile fields."""

    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr


class AdminPasswordUpdate(BaseModel):
    """Schema for changing own admin password."""

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class AdminSuperAdminUpdate(BaseModel):
    """Schema for updating super admin status of another admin."""

    is_super_admin: bool
