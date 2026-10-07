from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User
from schemas.user import LoginResponse, UserLogin, UserRegister, UserResponse
from utils.auth import create_access_token, get_current_user
from utils.security import hash_password, verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    new_user = User(
        name=user_data.name,
        organization_name=user_data.organization_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        phone=user_data.phone,
        role=user_data.role.value,
        donor_type=(
            user_data.donor_type.value
            if user_data.donor_type
            else None
        ),
        location=user_data.location,
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        ) from exc

    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.email == login_data.email)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password, or account type.",
        )

    if user.role != login_data.role.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password, or account type.",
        )

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password, or account type.",
        )

    access_token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "organization_name": user.organization_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "donor_type": user.donor_type,
            "location": user.location,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    }


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
