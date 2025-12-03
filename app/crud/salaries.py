from datetime import date
from sqlalchemy.orm import Session
from app.models import Salary

def get_salaries_for_period(
    db: Session,
    emp_no: int,
    start_date: date,
    end_date: Optional[date]),
):
    """
    Return all salary rows for emp_no that overlap [start_date, end_date].
    """
    return (
        db.query(Salary)
        .filter(Salary.emp_no == emp_no)
        .filter(Salary.from_date <= end_date)
        .filter(Salary.to_date >= start_date)
        .order_by(Salary.from_date)
        .all()
    )
