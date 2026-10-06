from datetime import datetime, timedelta, timezone
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "foodys-development-secret",
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user