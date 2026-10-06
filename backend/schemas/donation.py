from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class DonationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    donor_id: int
    food_name: str
    description: str | None
    category: str
    quantity: int
    unit: str
    prepared_at: datetime
    expiry_time: datetime
    pickup_address: str
    status: str
    created_at: datetime
    updated_at: datetime