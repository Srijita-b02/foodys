from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class Deliveries(Base):
    __tablename__ = "deliveries"

    __table_args__ = (
        CheckConstraint(
            "status IN ('assigned', 'picked_up', 'in_transit', 'delivered', 'cancelled')",
            name="ck_deliveries_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )

    assigned_ngo_member_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="assigned",
        index=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    pickup_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivery_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    match = relationship("Match")
    assigned_ngo_member = relationship("User")
