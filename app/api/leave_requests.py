from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app import schemas
from app.crud import leave_requests as crud_leave_requests

router = APIRouter(prefix="/leave-requests", tags=["leave-requests"])


@router.get("", response_model=List[schemas.LeaveRequest])
def list_leave_requests(
    emp_no: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return crud_leave_requests.get_leave_requests(
        db, emp_no=emp_no, status=status, skip=offset, limit=limit
    )


@router.post("", response_model=schemas.LeaveRequest, status_code=201)
def create_leave_request(
    leave_in: schemas.LeaveRequestCreate,
    db: Session = Depends(get_db),
):
    # Business rules like quota checks can be added here before persisting.
    return crud_leave_requests.create_leave_request(db, leave_in)


@router.get("/{leave_id}", response_model=schemas.LeaveRequest)
def get_leave_request(leave_id: int, db: Session = Depends(get_db)):
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
