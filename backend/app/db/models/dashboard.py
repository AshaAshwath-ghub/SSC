"""
Dashboard models for UI builder feature.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Integer, ForeignKey, Text, JSON, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin


class Dashboard(Base, TimestampMixin):
    """Dashboard model."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    route_slug: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)

    # Dashboard configuration
    grid_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # rows, columns, etc.
    theme_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # colors, fonts, etc.

    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    published_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    published_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<Dashboard(id={self.id}, name={self.name}, owner_id={self.owner_id})>"


class DashboardAccess(Base, TimestampMixin):
    """Dashboard access control."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dashboard_id: Mapped[int] = mapped_column(ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)

    # Either user_id or role_id should be set, not both
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=True)

    permission_level: Mapped[str] = mapped_column(String(20), nullable=False)  # view, edit, admin
    granted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        Index("idx_dashboard_user", "dashboard_id", "user_id"),
        Index("idx_dashboard_role", "dashboard_id", "role_id"),
        # Ensure either user_id or role_id is set, but not both
        # This is enforced in application logic
    )

    def __repr__(self) -> str:
        return f"<DashboardAccess(dashboard_id={self.dashboard_id}, permission={self.permission_level})>"
