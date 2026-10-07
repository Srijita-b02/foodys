from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from database.database import get_db
from models.food_request import FoodRequest
from models.user import User
from schemas.food_request import (
    FoodRequestCreate,
    FoodRequestResponse,
    FoodRequestUpdate,
    current_time_for,
)
from utils.auth import get_current_user, require_roles


router = APIRouter(
    prefix="/requests",
    tags=["Food Requests"],
)


def expire_open_requests(db: Session) -> None:
    """Keep expired requests as history while removing them from active lists."""

    now = datetime.now(timezone.utc)
    result = db.execute(
        update(FoodRequest)
        .where(
            FoodRequest.status == "open",
            FoodRequest.needed_before <= now,
        )
        .values(status="expired", updated_at=now)
        .execution_options(synchronize_session=False)
    )

    if result.rowcount:
        db.commit()


def get_request_or_404(request_id: int, db: Session) -> FoodRequest:
    food_request = db.get(FoodRequest, request_id)

    if food_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food request does not exist.",
        )

    return food_request


@router.post(
    "",
    response_model=FoodRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_food_request(
    request_data: FoodRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    food_request = FoodRequest(
        ngo_id=current_user.id,
        **request_data.model_dump(),
        status="open",
    )

    db.add(food_request)
    db.commit()
    db.refresh(food_request)

    return food_request


@router.get("", response_model=list[FoodRequestResponse])
def list_open_requests(
    category: str | None = None,
    location: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user
    expire_open_requests(db)

    query = select(FoodRequest).where(FoodRequest.status == "open")

    if category:
        query = query.where(FoodRequest.category == category)

    if location:
        query = query.where(FoodRequest.location == location)

    return db.scalars(query.order_by(FoodRequest.needed_before)).all()


@router.get("/my", response_model=list[FoodRequestResponse])
def list_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    expire_open_requests(db)

    query = (
        select(FoodRequest)
        .where(FoodRequest.ngo_id == current_user.id)
        .order_by(FoodRequest.created_at.desc())
    )

    return db.scalars(query).all()


@router.get("/{request_id}", response_model=FoodRequestResponse)
def get_food_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user
    expire_open_requests(db)
    return get_request_or_404(request_id, db)


@router.put("/{request_id}", response_model=FoodRequestResponse)
def update_food_request(
    request_id: int,
    request_data: FoodRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    expire_open_requests(db)
    food_request = get_request_or_404(request_id, db)

    if food_request.ngo_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can update only your own food requests.",
        )

    if food_request.status != "open":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only open food requests can be updated.",
        )

    updates = request_data.model_dump(exclude_unset=True)
    needed_before = updates.get("needed_before", food_request.needed_before)

    if needed_before <= current_time_for(needed_before):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Needed-before time must be in the future.",
        )

    for field, value in updates.items():
        setattr(food_request, field, value)

    db.commit()
    db.refresh(food_request)

    return food_request


@router.delete("/{request_id}", response_model=FoodRequestResponse)
def cancel_food_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ngo")),
):
    expire_open_requests(db)
    food_request = get_request_or_404(request_id, db)

    if food_request.ngo_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can cancel only your own food requests.",
        )

    if food_request.status != "open":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only open food requests can be cancelled.",
        )

    food_request.status = "cancelled"
    db.commit()
    db.refresh(food_request)

    return food_request
