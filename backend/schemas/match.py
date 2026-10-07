from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MatchStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DirectReservationCreate(BaseModel):
    donation_id: int = Field(gt=0)
    allocated_quantity: int = Field(gt=0)


class RequestMatchCreate(BaseModel):
    donation_id: int = Field(gt=0)
    request_id: int = Field(gt=0)
    allocated_quantity: int = Field(gt=0)


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    donation_id: int
    request_id: int | None
    ngo_id: int
    allocated_quantity: int
    status: MatchStatus
    created_at: datetime
    updated_at: datetime
