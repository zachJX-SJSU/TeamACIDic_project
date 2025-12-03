from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.db import get_db
from app.crud import auth as crud_auth

from fastapi.security import OAuth2PasswordRequestForm
from app.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.security import verify_password, create_access_token
from app import models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.AuthUser).filter(models.AuthUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # determine roles
    is_manager = db.query(models.DeptManager).filter(
        models.DeptManager.emp_no == user.emp_no,
        models.DeptManager.to_date >= date.today()
    ).first() is not None

    is_hr = bool(getattr(user, "is_hr_admin", False))

    token = create_access_token(
        {
            "emp_no": user.emp_no,
            "is_manager": is_manager,
            "is_hr_admin": is_hr,
        },
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"access_token": token}

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
