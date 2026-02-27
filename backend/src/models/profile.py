from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .consultant import Consultant
    from .admin import Admin


class Profile(Base):
    """Profile snapshot model"""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultant_id: Mapped[int] = mapped_column(Integer, ForeignKey("consultants.id"), index=True)
    profile_name: Mapped[str] = mapped_column(String(200))  # e.g., "Client XYZ - Data Engineering Role"

    # Snapshot of selected blocks (JSON)
    selected_block_ids: Mapped[str] = mapped_column(Text)  # JSON array
    profile_data: Mapped[str] = mapped_column(Text)  # Complete JSON snapshot

    created_by_admin_id: Mapped[int] = mapped_column(Integer, ForeignKey("admins.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    consultant: Mapped["Consultant"] = relationship("Consultant", back_populates="profiles")
    created_by: Mapped["Admin"] = relationship("Admin")
