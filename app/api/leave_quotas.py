from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app import schemas
from app.crud import leave_quotas as crud_leave_quotas

router = APIRouter(prefix="/leave-quotas", tags=["leave-quotas"])


@router.get("", response_model=List[schemas.LeaveQuota])
def list_leave_quotas(
    emp_no: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    leave_type_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    return crud_leave_quotas.get_leave_quotas(
        db, emp_no=emp_no, year=year, leave_type_id=leave_type_id
    )


@router.post("", response_model=schemas.LeaveQuota, status_code=201)
def create_leave_quota(
    quota_in: schemas.LeaveQuotaCreate,
    db: Session = Depends(get_db),
):
    return crud_leave_quotas.create_leave_quota(db, quota_in)


@router.get("/{emp_no}/{year}/{leave_type_id}", response_model=schemas.LeaveQuota)
def get_leave_quota(
    emp_no: int,
    year: int,
    leave_type_id: int,
    db: Session = Depends(get_db),
):
    db_quota = crud_leave_quotas.get_leave_quota(db, emp_no, year, leave_type_id)
    if not db_quota:
        raise HTTPException(status_code=404, detail="Leave quota not found")
    return db_quota


@router.put("/{emp_no}/{year}/{leave_type_id}", response_model=schemas.LeaveQuota)
def update_leave_quota(
    emp_no: int,
    year: int,
    leave_type_id: int,
    quota_in: schemas.LeaveQuotaUpdate,
    db: Session = Depends(get_db),
):
    db_quota = crud_leave_quotas.get_leave_quota(db, emp_no, year, leave_type_id)
    if not db_quota:
        raise HTTPException(status_code=404, detail="Leave quota not found")
    return crud_leave_quotas.update_leave_quota(db, db_quota, quota_in)


@router.delete("/{emp_no}/{year}/{leave_type_id}", status_code=204)
def delete_leave_quota(
    emp_no: int,
    year: int,
    leave_type_id: int,
    db: Session = Depends(get_db),
):
    db_quota = crud_leave_quotas.get_leave_quota(db, emp_no, year, leave_type_id)
    if not db_quota:
        raise HTTPException(status_code=404, detail="Leave quota not found")
    crud_leave_quotas.delete_leave_quota(db, db_quota)
    return None
