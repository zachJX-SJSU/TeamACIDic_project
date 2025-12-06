from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.security import decode_access_token
from app.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return TokenData(
        emp_no=payload["emp_no"],
        is_manager=payload["is_manager"],
        is_hr_admin=payload["is_hr_admin"]
    )

def require_manager(current: TokenData = Depends(get_current_user)):
    if not current.is_manager:
        raise HTTPException(status_code=403, detail="Manager role required")
    return current

def require_hr(current: TokenData = Depends(get_current_user)):
    if not current.is_hr_admin:
        raise HTTPException(status_code=403, detail="HR role required")
    return current
