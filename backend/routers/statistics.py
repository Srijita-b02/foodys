from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import Session

from database.database import get_db
from models.deliveries import Deliveries
from models.donation import Donation
from models.food_request import FoodRequest
from models.match import Match
from models.user import User
from schemas.statistics import ImpactStatisticsResponse
from utils.auth import get_current_user


router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/impact", response_model=ImpactStatisticsResponse)
def get_impact_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return database-computed impact totals for either authenticated role."""

    del current_user

    delivered_quantity = db.scalar(
        select(func.coalesce(func.sum(Match.allocated_quantity), 0))
        .join(Deliveries, Deliveries.match_id == Match.id)
        .where(Deliveries.status == "delivered")
    ) or 0

    completed_deliveries = db.scalar(
        select(func.count(Deliveries.id)).where(Deliveries.status == "delivered")
    ) or 0

    fulfilled_requests = db.scalar(
        select(func.count(FoodRequest.id)).where(
            FoodRequest.status == "fulfilled"
        )
    ) or 0

    completed_donations = db.scalar(
        select(func.count(Donation.id)).where(Donation.status == "delivered")
    ) or 0

    active_donors = db.scalar(
        select(func.count(distinct(User.id)))
        .join(Donation, Donation.donor_id == User.id)
        .where(
            User.role == "donor",
            Donation.status.notin_(["cancelled", "expired"]),
        )
    ) or 0

    active_ngos = db.scalar(
        select(func.count(distinct(User.id)))
        .outerjoin(FoodRequest, FoodRequest.ngo_id == User.id)
        .outerjoin(Match, Match.ngo_id == User.id)
        .where(
            User.role == "ngo",
            or_(FoodRequest.id.is_not(None), Match.id.is_not(None)),
        )
    ) or 0

    return ImpactStatisticsResponse(
        delivered_quantity=delivered_quantity,
        completed_deliveries=completed_deliveries,
        fulfilled_requests=fulfilled_requests,
        completed_donations=completed_donations,
        active_donors=active_donors,
        active_ngos=active_ngos,
    )
