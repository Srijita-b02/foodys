from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DonationCreate(BaseModel):
    food_name: str = Field(
        min_length=2,
        max_length=150,
    )

    description: str | None = None

    category: str = Field(
        min_length=2,
        max_length=50,
    )

    quantity: int = Field(
        gt=0,
    )

    unit: str = Field(
        min_length=1,
        max_length=30,
    )

    prepared_at: datetime

    expiry_time: datetime

    pickup_address: str = Field(
        min_length=2,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_expiry(self):
        if self.expiry_time <= self.prepared_at:
            raise ValueError("Expiry time must be later than preparation time.")

        return self


class DonationUpdate(BaseModel):
    food_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = None

    category: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    quantity: int | None = Field(
        default=None,
        gt=0,
    )

    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    prepared_at: datetime | None = None

    expiry_time: datetime | None = None

    pickup_address: str | None = Field(
        default=None,
        min_length=2,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_expiry(self):
        if (
            self.prepared_at is not None
            and self.expiry_time is not None
            and self.expiry_time <= self.prepared_at
        ):
            raise ValueError("Expiry time must be later than preparation time.")

        return self


class DonationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    donor_id: int
    food_name: str
    description: str | None
    category: str
    quantity: int
    remaining_quantity: int | None = Field(default=None, ge=0)
    unit: str
    prepared_at: datetime
    expiry_time: datetime
    pickup_address: str
    status: str
    created_at: datetime
    updated_at: datetime


class DonationAllocationResponse(BaseModel):
    match_id: int
    donation_id: int
    request_id: int | None
    allocated_quantity: int = Field(gt=0)
    match_status: str
    delivery_status: str
    assigned_at: datetime
    pickup_time: datetime | None
    delivery_time: datetime | None
