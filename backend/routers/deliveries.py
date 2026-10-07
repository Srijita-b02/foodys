from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.database import get_db
from models.deliveries import Deliveries
from models.donation import Donation
from models.food_request import FoodRequest
from models.match import Match
from models.user import User
from schemas.deliveries import DeliveriesRead, DeliveriesStatusUpdate
from utils.auth import require_roles


router = APIRouter(
    prefix="/deliveries",
    tags=["Deliveries"],
)


VALID_TRANSITIONS = {
    "assigned": {"picked_up"},
    "picked_up": {"in_transit"},
    "in_transit": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


def _check_access(
    deliveries: Deliveries,
    current_user: User,
):
    if current_user.role != "ngo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only NGO members can access deliveries.",
        )

    if deliveries.assigned_ngo_member_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this delivery.",
        )


def _recalculate_donation(
    db: Session,
    donation: Donation,
):
    completed = db.scalar(
        select(func.coalesce(func.sum(Match.allocated_quantity), 0))
        .join(
            Deliveries,
            Deliveries.match_id == Match.id,
        )
        .where(
            Match.donation_id == donation.id,
            Match.status != "cancelled",
            Deliveries.status == "delivered",
        )
    ) or 0

    allocated = db.scalar(
        select(func.coalesce(func.sum(Match.allocated_quantity), 0))
        .where(
            Match.donation_id == donation.id,
            Match.status != "cancelled",
        )
    ) or 0

    if completed >= donation.quantity:
        donation.status = "delivered"
    elif allocated >= donation.quantity:
        donation.status = "matched"
    else:
        donation.status = "available"


def _recalculate_food_request(
    db: Session,
    food_request: FoodRequest,
):
    completed = db.scalar(
        select(func.coalesce(func.sum(Match.allocated_quantity), 0))
        .join(
            Deliveries,
            Deliveries.match_id == Match.id,
        )
        .where(
            Match.request_id == food_request.id,
            Match.status != "cancelled",
            Deliveries.status == "delivered",
        )
    ) or 0

    allocated = db.scalar(
        select(func.coalesce(func.sum(Match.allocated_quantity), 0))
        .where(
            Match.request_id == food_request.id,
            Match.status != "cancelled",
        )
    ) or 0

    if completed >= food_request.quantity:
        food_request.status = "fulfilled"
    elif allocated >= food_request.quantity:
        food_request.status = "matched"
    else:
        food_request.status = "open"


# ------------------------------------------------------------------
# Functions used directly by tests
# ------------------------------------------------------------------


def get_deliveries(
    delivery_id: int,
    db: Session,
    current_user: User,
):
    deliveries = db.get(Deliveries, delivery_id)

    if deliveries is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found.",
        )

    _check_access(deliveries, current_user)

    return deliveries


def list_my_deliveries(
    db: Session,
    current_user: User,
):
    if current_user.role != "ngo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only NGO members can access deliveries.",
        )

    return list(
        db.scalars(
            select(Deliveries)
            .where(
                Deliveries.assigned_ngo_member_id == current_user.id
            )
            .order_by(Deliveries.created_at.desc())
        ).all()
    )


def update_deliveries_status(
    delivery_id: int,
    payload: DeliveriesStatusUpdate,
    db: Session,
    current_user: User,
):
    deliveries = db.scalar(
        select(Deliveries)
        .where(Deliveries.id == delivery_id)
        .with_for_update()
    )

    if deliveries is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found.",
        )

    _check_access(deliveries, current_user)

    old_status = deliveries.status
    new_status = payload.status

    # Reject skipped or backward transitions.
    if new_status not in VALID_TRANSITIONS.get(old_status, set()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid delivery status transition: "
                f"{old_status} -> {new_status}."
            ),
        )

    now = datetime.now(timezone.utc)

    # --------------------------------------------------------------
    # assigned -> picked_up
    # --------------------------------------------------------------
    if new_status == "picked_up":
        deliveries.status = "picked_up"
        deliveries.pickup_time = now

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(deliveries)
        return deliveries

    # --------------------------------------------------------------
    # picked_up -> in_transit
    # --------------------------------------------------------------
    if new_status == "in_transit":
        deliveries.status = "in_transit"

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(deliveries)
        return deliveries

    # --------------------------------------------------------------
    # in_transit -> delivered
    #
    # Everything below must succeed together:
    #
    # 1. Delivery -> delivered
    # 2. deliveries_time set
    # 3. Match -> completed
    # 4. Donation recalculated
    # 5. FoodRequest recalculated
    #
    # If anything fails, everything is rolled back.
    # --------------------------------------------------------------
    try:
        deliveries.status = "delivered"
        deliveries.deliveries_time = now

        match = db.scalar(
            select(Match)
            .where(Match.id == deliveries.match_id)
            .with_for_update()
        )

        if match is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The delivery's match no longer exists.",
            )

        match.status = "completed"

        donation = db.scalar(
            select(Donation)
            .where(Donation.id == match.donation_id)
            .with_for_update()
        )

        if donation is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The matched donation no longer exists.",
            )

        _recalculate_donation(
            db,
            donation,
        )

        if match.request_id is not None:
            food_request = db.scalar(
                select(FoodRequest)
                .where(FoodRequest.id == match.request_id)
                .with_for_update()
            )

            if food_request is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The matched food request no longer exists.",
                )

            _recalculate_food_request(
                db,
                food_request,
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    db.refresh(deliveries)

    return deliveries


# ------------------------------------------------------------------
# FastAPI endpoints
# ------------------------------------------------------------------


@router.get(
    "/my",
    response_model=list[DeliveriesRead],
)
def api_list_my_deliveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    return list_my_deliveries(
        db,
        current_user,
    )


@router.get(
    "/{delivery_id}",
    response_model=DeliveriesRead,
)
def api_get_deliveries(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    return get_deliveries(
        delivery_id,
        db,
        current_user,
    )


@router.patch(
    "/{delivery_id}/status",
    response_model=DeliveriesRead,
)
def api_update_deliveries_status(
    delivery_id: int,
    payload: DeliveriesStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    return update_deliveries_status(
        delivery_id,
        payload,
        db,
        current_user,
    )