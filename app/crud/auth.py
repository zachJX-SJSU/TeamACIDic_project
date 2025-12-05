from typing import Optional

from sqlalchemy.orm import Session

from app import models
from app.security import verify_password, hash_password


def get_auth_user_by_username(db: Session, username: str) -> Optional[models.AuthUser]:
    return (
        db.query(models.AuthUser)
        .filter(models.AuthUser.username == username)
        .first()
    )


def get_auth_user_by_emp_no(db: Session, emp_no: int) -> Optional[models.AuthUser]:
    return (
        db.query(models.AuthUser)
        .filter(models.AuthUser.emp_no == emp_no)
        .first()
    )


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.AuthUser]:
    """
    Return AuthUser if username/password are correct and user is active,
    otherwise return None.
    """
    user = get_auth_user_by_username(db, username)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def change_user_password(db: Session, emp_no: int, current_password: str, new_password: str) -> tuple[bool, str]:
    """
    Change user password after verifying current password.
    Returns tuple of (success: bool, error_message: str).
    Error message is empty string if successful.
    """
    user = get_auth_user_by_emp_no(db, emp_no)
    if not user:
        return False, "User not found"
    
    # Check if user is active
    if not user.is_active:
        return False, "User account is inactive"
    
    # Verify current password
    if not verify_password(current_password, user.password_hash):
        return False, "Current password is incorrect"
    
    # Check if new password is same as current password
    if verify_password(new_password, user.password_hash):
        return False, "New password must be different from current password"
    
    # Hash and update new password
    user.password_hash = hash_password(new_password)
    db.commit()
    return True, ""
