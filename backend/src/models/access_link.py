from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .consultant import Consultant
    from .admin import Admin


class AccessLink(Base):
    """Temporary access link model"""

    __tablename__ = "access_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultant_id: Mapped[int] = mapped_column(Integer, ForeignKey("consultants.id"), index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # UUID
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_by_admin_id: Mapped[int] = mapped_column(Integer, ForeignKey("admins.id"))
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    consultant: Mapped["Consultant"] = relationship("Consultant", back_populates="access_links")
    created_by: Mapped["Admin"] = relationship("Admin")
