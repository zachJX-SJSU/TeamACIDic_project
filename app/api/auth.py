from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app import schemas
from app.crud import auth as crud_auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(
    credentials: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Basic username/password login.
    For now, just validates credentials and returns user info.
    Later we can extend this to issue a JWT access token.
    """
    user = crud_auth.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        # Generic error to avoid leaking which part is wrong
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return schemas.LoginResponse(
        username=user.username,
        emp_no=user.emp_no,
        message="login successful",
    )

#  TO-DO Add an endpoint for change password