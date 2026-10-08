from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from database.database import get_db
from models.deliveries import Deliveries
from models.donation import Donation
from models.food_request import FoodRequest
from models.match import Match
from models.user import User
from schemas.deliveries import DeliveriesStatusUpdate, DeliveryDetailsRead
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


def _delivery_details_query(current_user: User):
    donor_user = aliased(User)
    ngo_user = aliased(User)

    return (
        select(
            Deliveries,
            Match,
            Donation,
            FoodRequest,
            donor_user,
            ngo_user,
        )
        .join(Match, Match.id == Deliveries.match_id)
        .join(Donation, Donation.id == Match.donation_id)
        .outerjoin(FoodRequest, FoodRequest.id == Match.request_id)
        .join(donor_user, donor_user.id == Donation.donor_id)
        .join(ngo_user, ngo_user.id == Match.ngo_id)
        .where(Deliveries.assigned_ngo_member_id == current_user.id)
    )


def _to_delivery_details(row) -> DeliveryDetailsRead:
    deliveries, match, donation, food_request, donor_user, ngo_user = row

    return DeliveryDetailsRead(
        id=deliveries.id,
        match_id=deliveries.match_id,
        assigned_ngo_member_id=deliveries.assigned_ngo_member_id,
        status=deliveries.status,
        assigned_at=deliveries.assigned_at,
        pickup_time=deliveries.pickup_time,
        delivery_time=deliveries.delivery_time,
        created_at=deliveries.created_at,
        updated_at=deliveries.updated_at,
        donation_id=donation.id,
        request_id=match.request_id,
        allocated_quantity=match.allocated_quantity,
        match_status=match.status,
        food_name=donation.food_name,
        category=donation.category,
        unit=donation.unit,
        pickup_address=donation.pickup_address,
        expiry_time=donation.expiry_time,
        donor_name=donor_user.name,
        ngo_member_name=ngo_user.name,
        organization_name=ngo_user.organization_name,
        destination_location=(
            food_request.location if food_request else ngo_user.location
        ),
    )


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
    # 2. delivery_time set
    # 3. Match -> completed
    # 4. Donation recalculated
    # 5. FoodRequest recalculated
    #
    # If anything fails, everything is rolled back.
    # --------------------------------------------------------------
    try:
        deliveries.status = "delivered"
        deliveries.delivery_time = now

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

        # Production sessions disable autoflush. Persist the pending delivery
        # and match states before the aggregate queries recalculate related
        # donation and request statuses.
        db.flush()

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


def list_my_delivery_details(
    db: Session,
    current_user: User,
):
    if current_user.role != "ngo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only NGO members can access deliveries.",
        )

    rows = db.execute(
        _delivery_details_query(current_user).order_by(
            Deliveries.created_at.desc()
        )
    ).all()
    return [_to_delivery_details(row) for row in rows]


def get_delivery_details(
    delivery_id: int,
    db: Session,
    current_user: User,
):
    # Preserve the existing missing-record and assigned-member checks.
    get_deliveries(delivery_id, db, current_user)
    row = db.execute(
        _delivery_details_query(current_user).where(
            Deliveries.id == delivery_id
        )
    ).one()
    return _to_delivery_details(row)


# ------------------------------------------------------------------
# FastAPI endpoints
# ------------------------------------------------------------------


@router.get(
    "/my",
    response_model=list[DeliveryDetailsRead],
)
def api_list_my_deliveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    return list_my_delivery_details(
        db,
        current_user,
    )


@router.get(
    "/{delivery_id}",
    response_model=DeliveryDetailsRead,
)
def api_get_deliveries(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    return get_delivery_details(
        delivery_id,
        db,
        current_user,
    )


@router.patch(
    "/{delivery_id}/status",
    response_model=DeliveryDetailsRead,
)
def api_update_deliveries_status(
    delivery_id: int,
    payload: DeliveriesStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    update_deliveries_status(
        delivery_id,
        payload,
        db,
        current_user,
    )
    return get_delivery_details(
        delivery_id,
        db,
        current_user,
    )
