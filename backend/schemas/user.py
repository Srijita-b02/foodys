from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserRole(str, Enum):
    DONOR = "donor"
    NGO = "ngo"


class DonorType(str, Enum):
    INDIVIDUAL = "individual"
    RESTAURANT = "restaurant"


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    organization_name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str = Field(min_length=7, max_length=20)
    role: UserRole
    donor_type: DonorType | None = None
    location: str = Field(min_length=2, max_length=500)

    @model_validator(mode="after")
    def validate_account_type(self):
        if self.role == UserRole.DONOR and self.donor_type is None:
            raise ValueError(
                "Donor type is required for donor accounts."
            )

        if self.role == UserRole.DONOR and self.organization_name is not None:
            raise ValueError(
                "Organization name can only be used for NGO accounts."
            )

        if self.role == UserRole.NGO and self.organization_name is None:
            raise ValueError(
                "Organization name is required for NGO accounts."
            )

        if self.role == UserRole.NGO and self.donor_type is not None:
            raise ValueError(
                "Donor type can only be used for donor accounts."
            )

        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    role: UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    organization_name: str | None
    email: EmailStr
    phone: str
    role: UserRole
    donor_type: DonorType | None
    location: str
    created_at: datetime
    updated_at: datetime


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user: UserResponse
