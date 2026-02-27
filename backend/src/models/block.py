from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .consultant import Consultant


class Block(Base):
    """Content block model (polymorphic - single table inheritance)"""

    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultant_id: Mapped[int] = mapped_column(Integer, ForeignKey("consultants.id"), index=True)
    block_type: Mapped[str] = mapped_column(String(50))  # "project", "skill", "certification", "misc"

    # Common fields
    title: Mapped[str] = mapped_column(String(200))
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Type-specific fields (nullable, validated in schemas)
    # For Projects
    client_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    project_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str | None] = mapped_column(String(200), nullable=True)
    technologies: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as string
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_ongoing: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # For Skills
    proficiency_level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # For Misc
    misc_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # For Certifications
    issuing_organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    credential_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    consultant: Mapped["Consultant"] = relationship("Consultant", back_populates="blocks")

    __mapper_args__ = {"polymorphic_on": "block_type", "polymorphic_identity": "block"}
