from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('donor', 'ngo')",
            name="ck_users_role",
        ),
        CheckConstraint(
            "donor_type IS NULL OR donor_type IN ('individual', 'restaurant')",
            name="ck_users_donor_type",
        ),
        CheckConstraint(
            "(role = 'donor' AND donor_type IS NOT NULL "
            "AND organization_name IS NULL) OR "
            "(role = 'ngo' AND donor_type IS NULL "
            "AND organization_name IS NOT NULL)",
            name="ck_users_role_fields",
        ),
    )

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

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
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

    # Used only when role = "ngo". The name field stores the member name.
    organization_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    location: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
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
