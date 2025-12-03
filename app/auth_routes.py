# app/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app import models

router = APIRouter(prefix="/auth", tags=["auth"])

# Use bcrypt like the rest of the project
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # bcrypt only uses first 72 bytes, but we'll just keep it simple here
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Avoid bcrypt error if someone passes a super long string
    if plain_password is not None:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


# ---------- Pydantic schemas (request/response) ----------

class LoginRequest(BaseModel):
    username: str
    password: str = Field(max_length=72)


class LoginResponse(BaseModel):
    username: str
    emp_no: int | None = None
    role: str


class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str = Field(max_length=72)
    new_password: str = Field(min_length=8, max_length=72)


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)
    emp_no: int | None = None
    role: str = "EMPLOYEE"


class UserOut(BaseModel):
    username: str
    emp_no: int | None = None
    role: str

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


# ---------- Routes ----------

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Basic login:
    - Look up auth_users by username
    - Check bcrypt password
    - Return basic user info if ok
    """
    user = db.query(models.AuthUser).filter(
        models.AuthUser.username == payload.username
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")

    return LoginResponse(
        username=user.username,
        emp_no=user.emp_no,
        role=user.role,
    )


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db)):
    """
    Allow a user to change their password by providing:
    - username
    - old_password
    - new_password
    """
    user = db.query(models.AuthUser).filter(
        models.AuthUser.username == payload.username
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    user.password_hash = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


@router.post("/create-user", response_model=UserOut)
def create_user(payload: CreateUserRequest, db: Session = Depends(get_db)):
    """
    Create a new login account.
    In a real app this would be limited to HR/admin users only.
    """
    existing = db.query(models.AuthUser).filter(
        models.AuthUser.username == payload.username
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    password_hash = hash_password(payload.password)

    new_user = models.AuthUser(
        username=payload.username,
        password_hash=password_hash,
        emp_no=payload.emp_no,
        role=payload.role,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
