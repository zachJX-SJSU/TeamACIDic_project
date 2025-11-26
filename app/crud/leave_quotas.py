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
