from typing import Optional

from sqlalchemy.orm import Session

from app import models
from app.security import verify_password


def get_auth_user_by_username(db: Session, username: str) -> Optional[models.AuthUser]:
    return (
        db.query(models.AuthUser)
        .filter(models.AuthUser.username == username)
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
