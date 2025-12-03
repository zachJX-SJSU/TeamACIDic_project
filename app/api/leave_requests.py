import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app import schemas
from app.crud import leave_requests as crud_leave_requests

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leave-requests", tags=["leave-requests"])


@router.get("", response_model=List[schemas.LeaveRequest])
def list_leave_requests(
    emp_no: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    logger.info("GET /leave-requests called", extra={"emp_no": emp_no,"status": status, "limit": limit, "offset": offset})
    try:
        leave_requests = crud_leave_requests.get_leave_requests(
            db, emp_no=emp_no, status=status, skip=offset, limit=limit
        )
        return leave_requests
    except Exception as e:
        # Log the exception with stack trace
        logger.exception("Error in GET /leave-requests")
        # Let FastAPI/Uvicorn handle the actual response (500)
        raise


@router.post("", response_model=schemas.LeaveRequest, status_code=201)
def create_leave_request(
    leave_in: schemas.LeaveRequestCreate,
    db: Session = Depends(get_db),
):
    """
    Create a leave request.
    Validates quota availability before creating the request.
    Returns error with "Insufficient quota" if quota is not sufficient.
    """
    logger.info("POST /leave-requests called", extra={"leave_req":leave_in})
    try:
        leave_request = crud_leave_requests.create_leave_request(db, leave_in)
        return leave_request
    except Exception as e:
        # Log the exception with stack trace
        logger.exception("Error in POST /leave-requests")
        # Let FastAPI/Uvicorn handle the actual response (500)
        raise
    


@router.get("/{leave_id}", response_model=schemas.LeaveRequest)
def get_leave_request(leave_id: int, db: Session = Depends(get_db)):
    logger.info("GET leaveReq by id...", extra={"leave_id":leave_id})
    db_leave = crud_leave_requests.get_leave_request(db, leave_id)
    if not db_leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return db_leave


@router.put("/{leave_id}", response_model=schemas.LeaveRequest)
def update_leave_request(
    leave_id: int,
    leave_in: schemas.LeaveRequestUpdate,
    db: Session = Depends(get_db),
):
    logger.info("UPDATE leaveReq by id...", extra={"leave_id":leave_id, "leave_in": leave_in})
    db_leave = crud_leave_requests.get_leave_request(db, leave_id)
    if not db_leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return crud_leave_requests.update_leave_request(db, db_leave, leave_in)


@router.delete("/{leave_id}", status_code=204)
def delete_leave_request(leave_id: int, db: Session = Depends(get_db)):
    db_leave = crud_leave_requests.get_leave_request(db, leave_id)
    if not db_leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    crud_leave_requests.delete_leave_request(db, db_leave)
    return None


@router.patch("/{leave_id}/review", response_model=schemas.LeaveRequest)
def review_leave_request(
    leave_id: int,
    review_in: schemas.LeaveRequestReview,
    manager_emp_no: int = Query(..., description="Employee number of the reviewing manager"),
    db: Session = Depends(get_db),
):
    """
    Manager reviews (approves or rejects) a leave request.
    If approved, the quota is automatically deducted from employee's quota.
    Only pending requests can be reviewed.
    """
    return crud_leave_requests.review_leave_request(
        db, leave_id, review_in, manager_emp_no
    )
