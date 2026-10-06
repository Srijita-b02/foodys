from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="donor",
        index=True,
    )

    # Used only when role = "donor".
    # Allowed values: "individual" or "restaurant".
    donor_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Used only when role = "volunteer".
    # Points to the NGO that the volunteer belongs to.
    ngo_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
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

    # Donor -> donations
    donations = relationship(
        "Donation",
        back_populates="donor",
    )

    # NGO -> volunteers
    volunteers = relationship(
        "User",
        back_populates="ngo",
        foreign_keys=[ngo_id],
    )

    # Volunteer -> NGO
    ngo = relationship(
        "User",
        back_populates="volunteers",
        remote_side=[id],
        foreign_keys=[ngo_id],
    )