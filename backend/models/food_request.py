from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class FoodRequest(Base):
    __tablename__ = "food_requests"
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_food_requests_quantity_positive",
        ),
        CheckConstraint(
            "needed_before > created_at",
            name="ck_food_requests_deadline_after_creation",
        ),
        CheckConstraint(
            "status IN ('open', 'matched', 'fulfilled', 'cancelled', 'expired')",
            name="ck_food_requests_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    ngo_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    food_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    needed_before: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="open",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Kept unidirectional so Person A's User model does not need modification.
    ngo = relationship("User")
