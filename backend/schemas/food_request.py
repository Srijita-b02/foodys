from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FoodRequestStatus(str, Enum):
    OPEN = "open"
    MATCHED = "matched"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


def current_time_for(value: datetime) -> datetime:
    """Return now with the same timezone-awareness as the supplied value."""

    return datetime.now(value.tzinfo) if value.tzinfo else datetime.now()


class FoodRequestCreate(BaseModel):
    food_name: str = Field(min_length=2, max_length=150)
    category: str = Field(min_length=2, max_length=50)
    quantity: int = Field(gt=0)
    unit: str = Field(min_length=1, max_length=30)
    description: str | None = None
    location: str = Field(min_length=2, max_length=500)
    needed_before: datetime

    @model_validator(mode="after")
    def validate_deadline(self):
        if self.needed_before <= current_time_for(self.needed_before):
            raise ValueError("Needed-before time must be in the future.")

        return self


class FoodRequestUpdate(BaseModel):
    food_name: str | None = Field(default=None, min_length=2, max_length=150)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    quantity: int | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    description: str | None = None
    location: str | None = Field(default=None, min_length=2, max_length=500)
    needed_before: datetime | None = None

    @model_validator(mode="after")
    def validate_deadline(self):
        if (
            self.needed_before is not None
            and self.needed_before <= current_time_for(self.needed_before)
        ):
            raise ValueError("Needed-before time must be in the future.")

        return self


class FoodRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ngo_id: int
    food_name: str
    category: str
    quantity: int
    unit: str
    description: str | None
    location: str
    needed_before: datetime
    status: FoodRequestStatus
    created_at: datetime
    updated_at: datetime
