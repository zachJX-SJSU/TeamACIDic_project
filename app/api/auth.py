from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.security import hash_password, verify_password

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

@router.post("/change-password")
def change_password(
    payload: schemas.ChangePasswordRequest,
    db: Session = Depends(get_db),
):
    # 1. Get the user
    user = crud_auth.get_auth_user_by_username(db, payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Verify old password
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    # 3. Validate new password rules
    if len(payload.new_password) < 6 or len(payload.new_password) > 12:
        raise HTTPException(status_code=400, detail="Password must be 6–12 characters")

    if payload.new_password == payload.old_password:
        raise HTTPException(status_code=400, detail="New password must differ from the old password")

    # 4. Hash the new password and update
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    db.refresh(user)

    return {
        "message": "Password updated successfully",
        "username": user.username,
    }
