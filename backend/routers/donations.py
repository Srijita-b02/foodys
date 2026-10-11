from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from database.database import get_db
from models.donation import Donation
from models.deliveries import Deliveries
from models.match import Match
from models.user import User
from schemas.donation import (
    DonationAllocationResponse,
    DonationCreate,
    DonationResponse,
    DonationUpdate,
)
from utils.auth import get_current_user, require_roles


router = APIRouter(
    prefix="/donations",
    tags=["Donations"],
)


def attach_remaining_quantity(donation: Donation, db: Session) -> Donation:
    """Attach the quantity not yet allocated by non-cancelled matches."""

    allocated = db.scalar(
        select(func.coalesce(func.sum(Match.allocated_quantity), 0)).where(
            Match.donation_id == donation.id,
            Match.status != "cancelled",
        )
    ) or 0
    donation.remaining_quantity = max(donation.quantity - allocated, 0)
    return donation


def expire_available_donations(db: Session) -> None:
    """Mark currently available donations as expired when their time passes."""

    result = db.execute(
        update(Donation)
        .where(
            Donation.status == "available",
            Donation.expiry_time <= datetime.now(timezone.utc),
        )
        .values(status="expired", updated_at=datetime.now(timezone.utc))
        .execution_options(synchronize_session=False)
    )

    if result.rowcount:
        db.commit()


def get_donation_or_404(donation_id: int, db: Session) -> Donation:
    donation = db.get(Donation, donation_id)

    if donation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donation does not exist.",
        )

    return donation


@router.post(
    "",
    response_model=DonationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_donation(
    donation_data: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("donor")),
):
    donation = Donation(
        donor_id=current_user.id,
        **donation_data.model_dump(),
        status="available",
    )

    db.add(donation)
    db.commit()
    db.refresh(donation)

    return attach_remaining_quantity(donation, db)


@router.get("", response_model=list[DonationResponse])
def list_donations(
    category: str | None = None,
    pickup_address: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user
    expire_available_donations(db)

    query = select(Donation).where(Donation.status == "available")

    if category:
        query = query.where(Donation.category == category)

    if pickup_address:
        query = query.where(Donation.pickup_address == pickup_address)

    donations = db.scalars(query.order_by(Donation.expiry_time)).all()
    return [attach_remaining_quantity(donation, db) for donation in donations]


@router.get("/my", response_model=list[DonationResponse])
def list_my_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("donor")),
):
    expire_available_donations(db)

    query = (
        select(Donation)
        .where(Donation.donor_id == current_user.id)
        .order_by(Donation.created_at.desc())
    )

    donations = db.scalars(query).all()
    return [attach_remaining_quantity(donation, db) for donation in donations]


@router.get(
    "/my/allocations",
    response_model=list[DonationAllocationResponse],
)
def list_my_donation_allocations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("donor")),
):
    """Show delivery progress for every allocated part of a donor's food."""

    rows = db.execute(
        select(Match, Deliveries)
        .join(Donation, Donation.id == Match.donation_id)
        .join(Deliveries, Deliveries.match_id == Match.id)
        .where(Donation.donor_id == current_user.id)
        .order_by(Deliveries.created_at.desc())
    ).all()

    return [
        DonationAllocationResponse(
            match_id=match.id,
            donation_id=match.donation_id,
            request_id=match.request_id,
            allocated_quantity=match.allocated_quantity,
            match_status=match.status,
            delivery_status=delivery.status,
            assigned_at=delivery.assigned_at,
            pickup_time=delivery.pickup_time,
            delivery_time=delivery.delivery_time,
        )
        for match, delivery in rows
    ]


@router.get("/{donation_id}", response_model=DonationResponse)
def get_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user
    expire_available_donations(db)
    donation = get_donation_or_404(donation_id, db)
    return attach_remaining_quantity(donation, db)


@router.put("/{donation_id}", response_model=DonationResponse)
def update_donation(
    donation_id: int,
    donation_data: DonationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("donor")),
):
    expire_available_donations(db)
    donation = get_donation_or_404(donation_id, db)

    if donation.donor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can update only your own donations.",
        )

    if donation.status != "available":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only available donations can be updated.",
        )

    updates = donation_data.model_dump(exclude_unset=True)
    prepared_at = updates.get("prepared_at", donation.prepared_at)
    expiry_time = updates.get("expiry_time", donation.expiry_time)

    if expiry_time <= prepared_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expiry time must be later than preparation time.",
        )

    for field, value in updates.items():
        setattr(donation, field, value)

    db.commit()
    db.refresh(donation)

    return attach_remaining_quantity(donation, db)


@router.delete("/{donation_id}", response_model=DonationResponse)
def cancel_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("donor")),
):
    expire_available_donations(db)
    donation = get_donation_or_404(donation_id, db)

    if donation.donor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can cancel only your own donations.",
        )

    if donation.status != "available":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only available donations can be cancelled.",
        )

    donation.status = "cancelled"
    db.commit()
    db.refresh(donation)

    return attach_remaining_quantity(donation, db)
