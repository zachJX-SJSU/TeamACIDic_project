from datetime import date, datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud import leave_quotas
from app.crud import employees


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


def get_employee_manager(db: Session, emp_no: int) -> Optional[int]:
    """
    Find the manager of an employee by looking up their CURRENT department
    (latest assignment where to_date = '9999-01-01') and then finding 
    the current manager of that department.
    
    Edge cases handled:
    - Employee has no current department → returns None
    - Multiple current departments → uses latest (ORDER BY from_date DESC)
    - Department has no current manager → returns None
    - Multiple current managers → uses latest (ORDER BY from_date DESC)
    
    Returns the manager's emp_no, or None if not found.
    """
    # Find employee's CURRENT department (active assignment)
    # If multiple exist, get the one with the latest from_date
    dept_query = text("""
        SELECT dept_no 
        FROM dept_emp 
        WHERE emp_no = :emp_no 
        AND to_date = '9999-01-01'
        ORDER BY from_date DESC
        LIMIT 1
    """)
    
    result = db.execute(dept_query, {"emp_no": emp_no}).fetchone()
    
    if not result:
        return None  # Employee has no current department
    
    dept_no = result[0]
    
    # Find current manager of that department
    # If multiple managers exist (shouldn't happen for current), get the one with latest from_date
    manager_query = text("""
        SELECT emp_no 
        FROM dept_manager 
        WHERE dept_no = :dept_no 
        AND to_date = '9999-01-01'
        ORDER BY from_date DESC
        LIMIT 1
    """)
    
    manager_result = db.execute(manager_query, {"dept_no": dept_no}).fetchone()
    
    if not manager_result:
        return None  # Department has no current manager
    
    return manager_result[0]


def check_quota_availability(
    db: Session, emp_no: int, leave_type_id: int, days_requested: int, year: Optional[int] = None
) -> bool:
    """
    Check if employee has sufficient quota for the requested leave type.
    Unpaid leaves (type 1) don't require quota checks.
    Returns True if quota is sufficient, False otherwise.
    """
    # Unpaid leaves don't have quotas
    if leave_type_id == 1:
        return True
    
    # Only paid (0) and sick (2) have quotas
    if leave_type_id not in [0, 2]:
        raise ValueError(f"Invalid leave_type_id: {leave_type_id}")
    
    if year is None:
        year = date.today().year
    
    # Get or create quota with default values
    quota = leave_quotas.get_or_create_quota(db, emp_no, leave_type_id, year)
    
    # Check if available quota is sufficient
    return quota.annual_quota_days >= days_requested


def create_leave_request(
    db: Session, leave_in: schemas.LeaveRequestCreate
) -> models.EmployeeLeaveRequest:
    """
    Create a leave request with quota validation and automatic manager assignment.
    
    Edge cases handled:
    1. Invalid dates (end_date < start_date) → HTTPException 400
    2. Employee doesn't exist → HTTPException 404
    3. Employee has no current department → manager_emp_no = None
    4. Department has no manager → manager_emp_no = None
    5. Multiple current departments → uses latest
    6. Quota validation for paid/sick leaves
    7. Negative/zero days → prevented by date validation
    """
    # EDGE CASE 1: Validate employee exists
    employee = employees.get_employee(db, leave_in.emp_no)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with emp_no {leave_in.emp_no} not found"
        )
    
    # EDGE CASE 2: Validate dates
    if leave_in.end_date < leave_in.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after or equal to start_date"
        )
    
    # Compute days_requested as inclusive difference.
    days_requested = (leave_in.end_date - leave_in.start_date).days + 1
    
    # EDGE CASE 3: Ensure positive days (shouldn't happen if dates are valid, but safeguard)
    if days_requested <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request must be for at least 1 day"
        )
    
    # EDGE CASE 4: Validate quota availability (only for paid and sick leaves)
    if leave_in.leave_type_id in [0, 2]:  # paid or sick
        if not check_quota_availability(
            db, leave_in.emp_no, leave_in.leave_type_id, days_requested
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient quota"
            )
    
    # EDGE CASE 5: Find the employee's CURRENT manager automatically
    # Returns None if employee has no department or department has no manager
    manager_emp_no = get_employee_manager(db, leave_in.emp_no)
    
    leave = models.EmployeeLeaveRequest(
        emp_no=leave_in.emp_no,
        leave_type_id=leave_in.leave_type_id,
        start_date=leave_in.start_date,
        end_date=leave_in.end_date,
        days_requested=days_requested,
        # Use uppercase to align with DB ENUM values
        status="PENDING",
        requested_at=datetime.utcnow(),
        employee_comment=leave_in.employee_comment,
        manager_emp_no=manager_emp_no,  # Set automatically (may be None if no manager found)
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


def update_quota_on_approval(
    db: Session, leave_request: models.EmployeeLeaveRequest
) -> None:
    """
    Update quota when a leave request is approved.
    Deducts the requested days from the employee's quota.
    Only updates quota for paid (0) and sick (2) leave types.
    """
    # Only update quota for paid and sick leaves
    if leave_request.leave_type_id not in [0, 2]:
        return
    
    # Get the year from start_date
    year = leave_request.start_date.year
    
    # Get or create quota
    quota = leave_quotas.get_or_create_quota(
        db, leave_request.emp_no, leave_request.leave_type_id, year
    )
    
    # Deduct the requested days from quota
    quota.annual_quota_days -= leave_request.days_requested
    
    # Ensure quota doesn't go negative (safeguard, though validation should prevent this)
    if quota.annual_quota_days < 0:
        quota.annual_quota_days = 0
    
    db.add(quota)
    db.commit()


def update_leave_request(
    db: Session,
    db_leave: models.EmployeeLeaveRequest,
    leave_in: schemas.LeaveRequestUpdate,
) -> models.EmployeeLeaveRequest:
    data = leave_in.model_dump(exclude_unset=True)
    
    # Track if status changed to APPROVED
    status_changed_to_approved = (
        "status" in data 
        and data["status"] == "APPROVED" 
        and db_leave.status != "APPROVED"
    )
    
    # If dates change, recompute days_requested.
    if "start_date" in data or "end_date" in data:
        start_date = data.get("start_date", db_leave.start_date)
        end_date = data.get("end_date", db_leave.end_date)
        db_leave.days_requested = (end_date - start_date).days + 1
    
    for key, value in data.items():
        setattr(db_leave, key, value)
    
    # When status changes away from PENDING, set decided_at timestamp.
    if "status" in data and data["status"] in {"APPROVED", "REJECTED"}:
        db_leave.decided_at = datetime.utcnow()
    
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    
    # If status changed to APPROVED, update quota
    if status_changed_to_approved:
        update_quota_on_approval(db, db_leave)
    
    return db_leave


def delete_leave_request(db: Session, db_leave: models.EmployeeLeaveRequest) -> None:
    db.delete(db_leave)
    db.commit()


def review_leave_request(
    db: Session,
    leave_id: int,
    review_in: schemas.LeaveRequestReview,
    manager_emp_no: int,
) -> models.EmployeeLeaveRequest:
    """
    Manager reviews (approves or rejects) a leave request.
    If approved, quota is automatically deducted.
    """
    leave_request = get_leave_request(db, leave_id)
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    if leave_request.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leave request is already {leave_request.status}"
        )
    
    # Update the request
    leave_request.status = review_in.status
    leave_request.manager_emp_no = manager_emp_no
    leave_request.manager_comment = review_in.manager_comment
    leave_request.decided_at = datetime.utcnow()
    
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    
    # If APPROVED, update quota
    if review_in.status == "APPROVED":
        update_quota_on_approval(db, leave_request)
    
    return leave_request
