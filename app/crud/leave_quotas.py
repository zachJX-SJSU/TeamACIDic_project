from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from app import models, schemas


def get_leave_quota(
    db: Session, emp_no: int, year: int, leave_type_id: int
) -> Optional[models.EmployeeLeaveQuota]:
    return (
        db.query(models.EmployeeLeaveQuota)
        .filter(
            models.EmployeeLeaveQuota.emp_no == emp_no,
            models.EmployeeLeaveQuota.year == year,
            models.EmployeeLeaveQuota.leave_type_id == leave_type_id,
        )
        .first()
    )


def get_leave_quotas(
    db: Session,
    emp_no: Optional[int] = None,
    year: Optional[int] = None,
    leave_type_id: Optional[int] = None,
) -> List[models.EmployeeLeaveQuota]:
    q = db.query(models.EmployeeLeaveQuota)
    if emp_no is not None:
        q = q.filter(models.EmployeeLeaveQuota.emp_no == emp_no)
    if year is not None:
        q = q.filter(models.EmployeeLeaveQuota.year == year)
    if leave_type_id is not None:
        q = q.filter(models.EmployeeLeaveQuota.leave_type_id == leave_type_id)
    return q.all()


def create_leave_quota(
    db: Session, quota_in: schemas.LeaveQuotaCreate
) -> models.EmployeeLeaveQuota:
    quota = models.EmployeeLeaveQuota(**quota_in.model_dump())
    db.add(quota)
    db.commit()
    db.refresh(quota)
    return quota


def update_leave_quota(
    db: Session,
    db_quota: models.EmployeeLeaveQuota,
    quota_in: schemas.LeaveQuotaUpdate,
) -> models.EmployeeLeaveQuota:
    data = quota_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_quota, key, value)
    db.add(db_quota)
    db.commit()
    db.refresh(db_quota)
    return db_quota


def delete_leave_quota(db: Session, db_quota: models.EmployeeLeaveQuota) -> None:
    db.delete(db_quota)
    db.commit()


def get_or_create_quota(
    db: Session, emp_no: int, leave_type_id: int, year: Optional[int] = None
) -> models.EmployeeLeaveQuota:
    """
    Get existing quota or create with default values.
    Default quotas: sick=5 days, paid=10 days.
    Unpaid leaves (type 1) don't have quotas.
    """
    if year is None:
        year = date.today().year
    
    # Default quota values based on leave type
    default_quotas = {
        0: 10,  # paid leave
        2: 5,   # sick leave
    }
    
    if leave_type_id not in default_quotas:
        raise ValueError(f"Invalid leave_type_id {leave_type_id} for quota. Only paid (0) and sick (2) have quotas.")
    
    quota = get_leave_quota(db, emp_no, year, leave_type_id)
    
    if quota is None:
        # Create quota with default value
        quota = models.EmployeeLeaveQuota(
            emp_no=emp_no,
            year=year,
            leave_type_id=leave_type_id,
            annual_quota_days=default_quotas[leave_type_id],
        )
        db.add(quota)
        db.commit()
        db.refresh(quota)
    
    return quota
