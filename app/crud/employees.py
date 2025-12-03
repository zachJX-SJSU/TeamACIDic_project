from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import models, schemas
from app.security import hash_password
from datetime import date
from app.models import Employee

DEFAULT_SICK_LEAVE_QUOTA = 5
DEFAULT_PAID_LEAVE_QUOTA = 10

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
    # Break the input into "belongs on Employee" vs "belongs on other tables"
    data = employee_in.model_dump()

    dept_no = data.pop("dept_no")
    title = data.pop("title")
    starting_salary = data.pop("starting_salary")

    # data now only has fields that actually exist on models.Employee:
    # birth_date, first_name, last_name, gender, hire_date
    employee = models.Employee(**data)
    db.add(employee)
    db.flush()  # get auto-generated emp_no

    # ---- Auth user for this employee ----
    initials = (employee.first_name[0] + employee.last_name[0]).lower()
    username = f"{initials}_{employee.emp_no}"

    auth_user = models.AuthUser(
        emp_no=employee.emp_no,
        username=username,
        password_hash=hash_password("abc123"),
        is_active=1,
    )
    db.add(auth_user)

    start_date = employee.hire_date
    far_future = date(9999, 1, 1)

    # ---- Dept assignment (dept_emp) ----
    db.add(
        models.DeptEmp(
            emp_no=employee.emp_no,
            dept_no=dept_no,
            from_date=start_date,
            to_date=far_future,
        )
    )

    # ---- Starting salary (salaries) ----
    db.add(
        models.Salary(
            emp_no=employee.emp_no,
            salary=starting_salary,
            from_date=start_date,
            to_date=far_future,
        )
    )

    # ---- Starting title (titles) ----
    db.add(
        models.Title(
            emp_no=employee.emp_no,
            title=title,
            from_date=start_date,
            to_date=far_future,
        )
    )

    # ---- Initial leave quota (example: sick leave for hire year) ----
    hire_year = start_date.year
    db.add(
        models.EmployeeLeaveQuota(
            emp_no=employee.emp_no,
            year=hire_year,
            leave_type_id=2,  # sick_leave
            annual_quota_days=DEFAULT_SICK_LEAVE_QUOTA,
        )
    )
    db.add(
        models.EmployeeLeaveQuota(
            emp_no=employee.emp_no,
            year=hire_year,
            leave_type_id=0,  # paid_leave
            annual_quota_days=DEFAULT_PAID_LEAVE_QUOTA,
        )
    )

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