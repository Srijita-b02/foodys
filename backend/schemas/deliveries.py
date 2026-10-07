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
    delivery_time: datetime | None
    created_at: datetime
    updated_at: datetime


class DeliveryDetailsRead(DeliveriesRead):
    donation_id: int
    request_id: int | None
    allocated_quantity: int
    match_status: str
    food_name: str
    category: str
    unit: str
    pickup_address: str
    expiry_time: datetime
    donor_name: str
    ngo_member_name: str
    organization_name: str | None
    destination_location: str


class DeliveriesStatusUpdate(BaseModel):
    status: DeliveryStatus
