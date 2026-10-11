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
from schemas.match import (
    DirectReservationCreate,
    MatchResponse,
    RequestAcceptanceCreate,
    RequestMatchCreate,
)
from utils.auth import get_current_user, require_roles


router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
)


def _current_time_for(value: datetime) -> datetime:
    """Return now with the same timezone-awareness as a stored timestamp."""

    if value.tzinfo:
        return datetime.now(value.tzinfo)

    # SQLite removes timezone information in unit tests. Treat those stored
    # values as UTC, matching PostgreSQL's timezone-aware production columns.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _allocated_for_donation(db: Session, donation_id: int) -> int:
    return db.scalar(
        select(func.coalesce(func.sum(Match.allocated_quantity), 0)).where(
            Match.donation_id == donation_id,
            Match.status != "cancelled",
        )
    ) or 0


def _allocated_for_request(db: Session, request_id: int) -> int:
    return db.scalar(
        select(func.coalesce(func.sum(Match.allocated_quantity), 0)).where(
            Match.request_id == request_id,
            Match.status != "cancelled",
        )
    ) or 0


def _lock_available_donation(
    db: Session,
    donation_id: int,
) -> Donation:
    donation = db.scalar(
        select(Donation)
        .where(Donation.id == donation_id)
        .with_for_update()
    )

    if donation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donation does not exist.",
        )

    if (
        donation.status != "available"
        or donation.expiry_time <= _current_time_for(donation.expiry_time)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Donation is no longer available.",
        )

    return donation


def _create_match_and_delivery(
    db: Session,
    *,
    donation: Donation,
    request_id: int | None,
    ngo_member_id: int,
    allocated_quantity: int,
) -> Match:
    donation_allocated = _allocated_for_donation(db, donation.id)
    donation_remaining = donation.quantity - donation_allocated

    if allocated_quantity > donation_remaining:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Requested quantity exceeds the donation's remaining "
                f"quantity of {donation_remaining}."
            ),
        )

    match = Match(
        donation_id=donation.id,
        request_id=request_id,
        ngo_id=ngo_member_id,
        allocated_quantity=allocated_quantity,
        status="active",
    )
    db.add(match)
    db.flush()

    delivery = Deliveries(
        match_id=match.id,
        assigned_ngo_member_id=ngo_member_id,
        status="assigned",
    )
    db.add(delivery)

    if donation_allocated + allocated_quantity >= donation.quantity:
        donation.status = "matched"

    return match


def reserve_donation(
    payload: DirectReservationCreate,
    db: Session,
    current_user: User,
) -> Match:
    try:
        donation = _lock_available_donation(db, payload.donation_id)
        match = _create_match_and_delivery(
            db,
            donation=donation,
            request_id=None,
            ngo_member_id=current_user.id,
            allocated_quantity=payload.allocated_quantity,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(match)
    return match


def respond_to_request(
    payload: RequestMatchCreate,
    db: Session,
    current_user: User,
) -> Match:
    try:
        # Always lock the donation before the request so concurrent matching
        # operations acquire shared resources in a consistent order.
        donation = _lock_available_donation(db, payload.donation_id)

        if donation.donor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can match only your own donations.",
            )

        food_request = db.scalar(
            select(FoodRequest)
            .where(FoodRequest.id == payload.request_id)
            .with_for_update()
        )

        if food_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food request does not exist.",
            )

        if (
            food_request.status != "open"
            or food_request.needed_before
            <= _current_time_for(food_request.needed_before)
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Food request is no longer open.",
            )

        if donation.unit.strip().casefold() != food_request.unit.strip().casefold():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Donation unit must match the food request unit before "
                    "quantities can be allocated."
                ),
            )

        request_allocated = _allocated_for_request(db, food_request.id)
        request_remaining = food_request.quantity - request_allocated

        if payload.allocated_quantity > request_remaining:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Allocated quantity exceeds the request's remaining "
                    f"quantity of {request_remaining}."
                ),
            )

        match = _create_match_and_delivery(
            db,
            donation=donation,
            request_id=food_request.id,
            ngo_member_id=food_request.ngo_id,
            allocated_quantity=payload.allocated_quantity,
        )

        if request_allocated + payload.allocated_quantity >= food_request.quantity:
            food_request.status = "matched"

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(match)
    return match


def accept_request(
    payload: RequestAcceptanceCreate,
    db: Session,
    current_user: User,
) -> Match:
    """Create donor supply and match it to an NGO request atomically."""

    try:
        food_request = db.scalar(
            select(FoodRequest)
            .where(FoodRequest.id == payload.request_id)
            .with_for_update()
        )

        if food_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food request does not exist.",
            )

        now = _current_time_for(food_request.needed_before)
        if food_request.status != "open" or food_request.needed_before <= now:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Food request is no longer open.",
            )

        request_allocated = _allocated_for_request(db, food_request.id)
        request_remaining = food_request.quantity - request_allocated

        if payload.allocated_quantity > request_remaining:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Allocated quantity exceeds the request's remaining "
                    f"quantity of {request_remaining}."
                ),
            )

        donation = Donation(
            donor_id=current_user.id,
            food_name=food_request.food_name,
            description=food_request.description,
            category=food_request.category,
            quantity=payload.allocated_quantity,
            unit=food_request.unit,
            prepared_at=now,
            expiry_time=food_request.needed_before,
            pickup_address=current_user.location,
            status="available",
        )
        db.add(donation)
        db.flush()

        match = _create_match_and_delivery(
            db,
            donation=donation,
            request_id=food_request.id,
            ngo_member_id=food_request.ngo_id,
            allocated_quantity=payload.allocated_quantity,
        )

        if request_allocated + payload.allocated_quantity >= food_request.quantity:
            food_request.status = "matched"

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(match)
    return match


def _match_query_for_user(current_user: User):
    query = select(Match)

    if current_user.role == "ngo":
        return query.where(Match.ngo_id == current_user.id)

    if current_user.role == "donor":
        return query.join(Donation).where(Donation.donor_id == current_user.id)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view matches.",
    )


@router.post(
    "/reserve",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def api_reserve_donation(
    payload: DirectReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    return reserve_donation(payload, db, current_user)


@router.post(
    "/respond",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def api_respond_to_request(
    payload: RequestMatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("donor")),
):
    return respond_to_request(payload, db, current_user)


@router.post(
    "/accept-request",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def api_accept_request(
    payload: RequestAcceptanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("donor")),
):
    return accept_request(payload, db, current_user)


@router.get("", response_model=list[MatchResponse])
def list_my_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _match_query_for_user(current_user)
    return list(db.scalars(query.order_by(Match.created_at.desc())).all())


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    match = db.scalar(
        _match_query_for_user(current_user).where(Match.id == match_id)
    )

    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match does not exist or is not accessible.",
        )

    return match
