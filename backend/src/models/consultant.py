from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .block import Block
    from .access_link import AccessLink
    from .profile import Profile
    from .admin import Admin


class Consultant(Base):
    """Consultant model"""

    __tablename__ = "consultants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # General section
    role: Mapped[str | None] = mapped_column(String(200), nullable=True)
    focus_areas: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    motto: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_admin_id: Mapped[int] = mapped_column(Integer, ForeignKey("admins.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    blocks: Mapped[List["Block"]] = relationship(
        "Block", back_populates="consultant", cascade="all, delete-orphan"
    )
    access_links: Mapped[List["AccessLink"]] = relationship(
        "AccessLink", back_populates="consultant", cascade="all, delete-orphan"
    )
    profiles: Mapped[List["Profile"]] = relationship("Profile", back_populates="consultant")
    created_by: Mapped["Admin"] = relationship("Admin")
