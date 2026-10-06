from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserRole(str, Enum):
    DONOR = "donor"
    NGO = "ngo"
    VOLUNTEER = "volunteer"
    ADMIN = "admin"


class DonorType(str, Enum):
    INDIVIDUAL = "individual"
    RESTAURANT = "restaurant"


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=20)
    role: UserRole
    donor_type: DonorType | None = None
    address: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_account_type(self):
        if self.role == UserRole.DONOR and self.donor_type is None:
            raise ValueError(
                "Donor type is required for donor accounts."
            )

        if self.role != UserRole.DONOR and self.donor_type is not None:
            raise ValueError(
                "Donor type can only be used for donor accounts."
            )

        if self.role == UserRole.VOLUNTEER:
            raise ValueError(
                "Volunteer accounts are created through an NGO."
            )

        if self.role == UserRole.ADMIN:
            raise ValueError(
                "Admin accounts cannot be created through public registration."
            )

        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: str | None
    role: UserRole
    donor_type: DonorType | None
    ngo_id: int | None
    address: str | None
    created_at: datetime
    updated_at: datetime