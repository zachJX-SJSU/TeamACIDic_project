from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas


def get_leave_request(db: Session, leave_id: int) -> Optional[models.EmployeeLeaveRequest]:
    return (
        db.query(models.EmployeeLeaveRequest)
        .filter(models.EmployeeLeaveRequest.leave_id == leave_id)
        .first()
    )


def get_leave_requests(
    db: Session,
    emp_no: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[models.EmployeeLeaveRequest]:
    q = db.query(models.EmployeeLeaveRequest)
    if emp_no is not None:
        q = q.filter(models.EmployeeLeaveRequest.emp_no == emp_no)
    if status is not None:
        q = q.filter(models.EmployeeLeaveRequest.status == status)
    return (
        q.order_by(models.EmployeeLeaveRequest.requested_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_leave_request(
    db: Session, leave_in: schemas.LeaveRequestCreate
) -> models.EmployeeLeaveRequest:
    # Compute days_requested as inclusive difference.
    days_requested = (leave_in.end_date - leave_in.start_date).days + 1
    leave = models.EmployeeLeaveRequest(
        emp_no=leave_in.emp_no,
        leave_type_id=leave_in.leave_type_id,
        start_date=leave_in.start_date,
        end_date=leave_in.end_date,
        days_requested=days_requested,
        status="PENDING",
        requested_at=datetime.utcnow(),
        employee_comment=leave_in.employee_comment,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


def update_leave_request(
    db: Session,
    db_leave: models.EmployeeLeaveRequest,
    leave_in: schemas.LeaveRequestUpdate,
) -> models.EmployeeLeaveRequest:
    data = leave_in.model_dump(exclude_unset=True)
    # If dates change, recompute days_requested.
    if "start_date" in data or "end_date" in data:
        start_date = data.get("start_date", db_leave.start_date)
        end_date = data.get("end_date", db_leave.end_date)
        db_leave.days_requested = (end_date - start_date).days + 1
    for key, value in data.items():
        setattr(db_leave, key, value)
    # When status changes away from PENDING, set decided_at timestamp.
    if "status" in data and data["status"] in {"APPROVED", "REJECTED", "CANCELLED"}:
        db_leave.decided_at = datetime.utcnow()
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave


def delete_leave_request(db: Session, db_leave: models.EmployeeLeaveRequest) -> None:
    db.delete(db_leave)
    db.commit()
