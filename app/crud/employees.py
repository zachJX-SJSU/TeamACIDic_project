from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import models, schemas
from app.security import hash_password
from app.models import Employee


def get_employee(db: Session, emp_no: int) -> Optional[models.Employee]:
    return db.query(models.Employee).filter(models.Employee.emp_no == emp_no).first()


def get_employees(db: Session, skip: int = 0, limit: int = 50) -> List[models.Employee]:
    return (
        db.query(models.Employee)
        .order_by(models.Employee.emp_no)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_employee(db: Session, employee_in: schemas.EmployeeCreate) -> models.Employee:
    # 1. Create the Employee row
    employee = models.Employee(**employee_in.model_dump())
    db.add(employee)
    db.flush()  # get employee.emp_no without committing yet

    # 2. Create matching AuthUser row with initials_empNo and default password "abc123"
    initials = (employee.first_name[0] + employee.last_name[0]).lower()
    username = f"{initials}_{employee.emp_no}"

    auth_user = models.AuthUser(
        emp_no=employee.emp_no,
        username=username,
        password_hash=hash_password("abc123"),
        is_active=1,
    )
    db.add(auth_user)

    # 3. Commit both in a single transaction
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(
    db: Session, db_employee: models.Employee, employee_in: schemas.EmployeeUpdate
) -> models.Employee:
    data = employee_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_employee, key, value)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, db_employee: models.Employee) -> None:
    db.delete(db_employee)
    db.commit()

def search_employees_by_name(
    db: Session,
    first_name: str,
    last_name: str,
    limit: int = 10,
    offset: int = 0,
) -> List[Employee]:
    """
    Search employees whose first_name and/or last_name START WITH the given prefixes.
    Case-insensitive. Empty string means 'no filter' for that field.
    """
    query = db.query(Employee)

    if first_name:
        query = query.filter(
            func.lower(Employee.first_name).like(func.lower(first_name) + "%")
        )

    if last_name:
        query = query.filter(
            func.lower(Employee.last_name).like(func.lower(last_name) + "%")
        )

    return (
        query
        .order_by(Employee.first_name, Employee.last_name, Employee.emp_no)
        .limit(limit)
        .offset(offset)
        .all()
    )