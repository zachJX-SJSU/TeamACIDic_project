from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import date, datetime
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.db import get_db
from app.crud.salaries import get_salaries_for_period
from app.schemas import SalaryPeriod

from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/employees",
    tags=["salary"]
)

far_future = date(9999, 1, 1)

@router.get("/{emp_no}/salaries", response_model=List[SalaryPeriod], dependencies=[Depends(get_current_user)])
def get_employee_salaries(
    emp_no: int,
    start_date: date = Query(..., description="Start of period (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(..., default=far_future, description="End of period (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if user.emp_no != emp_no and not user.is_hr_admin:
        raise HTTPException(403, "Not allowed to view another employee’s salary")
    # Basic validation
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")

    rows = get_salaries_for_period(
        db=db,
        emp_no=emp_no,
        start_date=start_date,
        end_date=end_date,
    )

    # Map ORM rows to response schema
    return [
        SalaryPeriod(
            salary=row.salary,
            start_date=row.from_date,
            end_date=row.to_date,
        )
        for row in rows
    ]

