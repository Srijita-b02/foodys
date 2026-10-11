from pydantic import BaseModel, Field


class ImpactStatisticsResponse(BaseModel):
    delivered_quantity: int = Field(ge=0)
    completed_deliveries: int = Field(ge=0)
    fulfilled_requests: int = Field(ge=0)
    completed_donations: int = Field(ge=0)
    active_donors: int = Field(ge=0)
    active_ngos: int = Field(ge=0)
