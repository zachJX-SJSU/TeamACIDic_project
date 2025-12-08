from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.db import get_db
from app.crud import auth as crud_auth
from app.dependencies.auth import get_current_user

from fastapi.security import OAuth2PasswordRequestForm
from app.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.security import verify_password, create_access_token
from app import models, schemas

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"/login called, username: {form_data.username}")
    user = db.query(models.AuthUser).filter(models.AuthUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        logger.info(f"/login failed, Invalid credentials, username: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # determine roles
    is_manager = db.query(models.DeptManager).filter(
        models.DeptManager.emp_no == user.emp_no,
        models.DeptManager.to_date >= date.today()
    ).first() is not None

    is_hr = bool(getattr(user, "is_hr_admin", False))

    logger.info(f"/login success, is_manager: {is_manager}, is_hr: {is_hr}")

    token = create_access_token(
        {
            "emp_no": user.emp_no,
            "is_manager": is_manager,
            "is_hr_admin": is_hr,
        },
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"access_token": token}


@router.post("/change-password")
def change_password(
    request: schemas.ChangePasswordRequest,
    current_user: schemas.TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the current user's password.
    Requires authentication and verification of current password.
    Validates that new password is different from current password.
    """
    logger.info(f"/change-password called for emp_no: {current_user.emp_no}")
    
    success, error_message = crud_auth.change_user_password(
        db,
        current_user.emp_no,
        request.current_password,
        request.new_password
    )
    
    if not success:
        logger.info(f"/change-password failed for emp_no: {current_user.emp_no}, reason: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    logger.info(f"/change-password success for emp_no: {current_user.emp_no}")
    return {"message": "Password changed successfully"}


# @router.post("/login", response_model=schemas.LoginResponse)
# def login(
#     credentials: schemas.LoginRequest,
#     db: Session = Depends(get_db),
# ):
#     """
#     Basic username/password login.
#     For now, just validates credentials and returns user info.
#     Later we can extend this to issue a JWT access token.
#     """
#     user = crud_auth.authenticate_user(db, credentials.username, credentials.password)
#     if not user:
#         # Generic error to avoid leaking which part is wrong
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid username or password",
#         )

#     return schemas.LoginResponse(
#         username=user.username,
#         emp_no=user.emp_no,
#         message="login successful",
#     )
