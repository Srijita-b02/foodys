from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


DeliveryStatus = Literal[
    "assigned",
    "picked_up",
    "in_transit",
    "delivered",
    "cancelled",
]


class DeliveriesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    assigned_ngo_member_id: int
    status: DeliveryStatus
    assigned_at: datetime
    pickup_time: datetime | None
    deliveries_time: datetime | None
    created_at: datetime
    updated_at: datetime


class DeliveriesStatusUpdate(BaseModel):
    status: DeliveryStatus